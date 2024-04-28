from matplotlib import pyplot as plt
import pickle
import time
import numpy as np
from scipy.interpolate import interp1d

dataFileName = 'checkpoints/2024_04_22-10h_21m-stayed_nights_4.pickle'
monthsInAYear = ['January',
                 'February',
                 'March',
                 'April',
                 'May',
                 'June',
                 'July',
                 'August',
                 'September',
                 'October',
                 'November',
                 'December']


def GetData():
    # Open the pickle file in binary read mode
    with open(dataFileName, 'rb') as f:
        # Load the pickled object from the file
        data = pickle.load(f)
    return data

# Returns an array of arrays of price data and an array of string labels.
# Missing data is just set to "None"
def CleanDataAndOutputAsLists(dataValues):
    studioLabels = []
    for someVal in dataValues:
        if someVal == -1:
            continue
        studioLabels = [' '.join(s.split()) for s in someVal.keys()]
        break

    dataArrays = {label: [] for label in studioLabels}
    for i, someVal in enumerate(dataValues):
        for label in studioLabels:
            if not isinstance(someVal, dict):
                dataArrays[label].append(None)
            elif label not in someVal.keys():
                # If the value is empty (because I moved the cursor lol), just use previous day's value.
                prevValue = dataValues[i-1][label]
                print('<<INTERPOLATING>> Interpolating value for studio type of {0} for index {1} with value of {2}'.format(label, i, prevValue))
                dataArrays[label].append(None if prevValue == -1 else prevValue)

            elif someVal[label] < 0:
                dataArrays[label].append(None)
            else:
                dataArrays[label].append(someVal[label])

    # print('Got the denormalized data here: {0}'.format(dataArrays))
    return dataArrays

def GetCleanedXLabels(keysList):
    xlabels = [str(dateTuple[0][0:3])+'-'+str(dateTuple[1])+'-'+str(dateTuple[2][2::]) for dateTuple in keysList]
    # # Our processor had a small bug. The first of each month would be of the previous month. The fix is fairly simple.
    # for label in xlabels:
    #     day = int(label.split('-')[1])
    #     if day == 1:
    #         print(label)
    return xlabels


def GetPeriodicTicksAndLabels(xData, allLabels):
    # Basically, just return a tick for every 1st and 15th of every month.
    reducedTicks = []
    reducedLabels = []
    print(allLabels)
    for i, label in enumerate(allLabels):
        
        day = int(label.split('-')[1])
        print(label)
        print(day)
        if day == 1 or day == 15:
            reducedTicks.append(xData[i])
            reducedLabels.append(allLabels[i])
    print(reducedTicks)
    print(reducedLabels)
    return reducedTicks, reducedLabels
    
def RemoveSpuriousOnesAndCleanMonths(data):
    keysList = list(data.keys())
    valuesList = list(data.values())
    stillProcessing = True
    while stillProcessing:
        stillProcessing = False
        prevDay = keysList[0][1]
        for i, key in enumerate(keysList[1:-1], start=1):
            print('i is {0}'.format(i))
            curDay = key[1]
            print('prev and cur day?')
            print(prevDay)
            print(curDay)
            # print('prev and cur (real) day?')
            # curDay = keysList[i][1]
            # print(prevDay)
            # print(curDay)
            curMonth = key[0]
            nextMonth = keysList[i+1][0]
            if curDay - prevDay != 1:
                prevMonth = keysList[i-1][0]
                nextDay = keysList[i+1][1]

                # 2 options: 1) the next element is the next day of the next month, e.g. Jan-31-24, Jan-1-24, Feb-2-24
                #            2) the next element is the next day of the previous segment, e.g. Jan-12-24, Jan-1-24, Jan-13-24     
                
                print('prev tuple: {0}'.format(keysList[i-1]))
                print('cur tuple: {0}'.format(keysList[i]))
                print('next tuple: {0}'.format(keysList[i+1]))
                if nextDay - prevDay == 1:
                    print('FOUND A SITUATION 2')
                    # In this case, eject this element
                    keysList.pop(i)
                    valuesList.pop(i)
                elif curDay < prevDay and curMonth is not nextMonth:
                    print('FOUND A SITUATION 1')
                    # In this case, change the current month ot the nextMonth
                    newTuple = list(keysList[i])
                    newTuple[0] = nextMonth
                    keysList[i] = tuple(newTuple)
                    # raise ValueError("This is a ValueError exception")
                else:
                    print('This is probably a normal month transition')
                    prevDay = curDay
                    continue
                stillProcessing = True
                prevDay = curDay
                break
            prevDay = curDay
    return keysList, valuesList
            
def IsInterestingType(studioName):
    print('what is studio name: {0}'.format(studioName))
    return 'Village Studio' == studioName or 'Courtyard Studio' == studioName

def GetVacanciesPerTick(xTicks, xData, yData):
    vacancies = [0 for i in range(len(xTicks))]
    tickIndex = 0
    for i, x in enumerate(xData):
        if tickIndex < len(xTicks) - 1:
            distanceToCur = abs(xTicks[tickIndex] - x)
            distanceToNext = abs(xTicks[tickIndex+1] - x)
            if distanceToCur > distanceToNext:
                tickIndex += 1
        if yData[i] is None:
            vacancies[tickIndex] += 1
    return vacancies

def GetAverageRatePerTick(xTicks, xData, yData):
    costSum = [0 for i in range(len(xTicks))]
    divider = [0 for i in range(len(xTicks))]
    tickIndex = 0
    for i, x in enumerate(xData):
        if tickIndex < len(xTicks) - 1:
            distanceToCur = abs(xTicks[tickIndex] - x)
            distanceToNext = abs(xTicks[tickIndex+1] - x)
            if distanceToCur > distanceToNext:
                tickIndex += 1
        
        costSum[tickIndex] += yData[i]
        divider[tickIndex] += 1
    rentalRates = [costSum[i] / divider[i] for i in range(len(costSum))]

    return rentalRates

def InterpolateYData(xData, yData):
    # Filter out None values and prepare valid points for interpolation
    x_valid = [xi for xi, yi in zip(xData, yData) if yi is not None]
    y_valid = [yi for yi in yData if yi is not None]

    print('XX<<<>>> ')
    print(len(x_valid))
    print((len(y_valid)))

    # Convert lists to numpy arrays
    x_valid = np.array(x_valid)
    y_valid = np.array(y_valid)

    # Create interpolation function
    f = interp1d(x_valid, y_valid, kind='linear', fill_value='extrapolate')

    # Use the function to interpolate all x values
    y_interpolated = f(xData)
    return list(y_interpolated)


if __name__ == "__main__":
    print('Starting visualization...')

    data = GetData()

    # Get rid of the supurious -1- pieces of data.
    keysList, valueList = RemoveSpuriousOnesAndCleanMonths(data)

    # Cut short our data to just a year.
    daysToKeep = 366
    keysList = keysList[:daysToKeep]
    valueList = valueList[:daysToKeep]

    # Clean the xData
    xDataUnix = [int(i[3]) for i in keysList]
    xDataRawCount = [i for i in range(len(keysList))]
    xLabelDayYear = GetCleanedXLabels(keysList)
    xTicks, xTickLabels = GetPeriodicTicksAndLabels(xDataRawCount, xLabelDayYear)

    # Clean the yData
    yDataDictionary = CleanDataAndOutputAsLists(valueList)
    interpYDataDictionary = {}
    for label in yDataDictionary.keys():
        interpYDataDictionary[label] = InterpolateYData(xDataRawCount, yDataDictionary[label])

    print('Graph 1: Print a plot of price per time, excluding times when units are not available')
    plt.figure()
    for yData in yDataDictionary.values():
        plt.plot(xDataRawCount, yData)
    plt.legend(yDataDictionary.keys())
    plt.xticks(ticks=xTicks, labels=xTickLabels, rotation=45)
    plt.xlabel('Time (Date)')
    plt.ylabel('Price (¥)')
    plt.title('Price Over Time')
    plt.grid()

    print('Graph 2: similar to Graph 1, but only for the village and courtyard studio, with interpolated values')
    plt.figure()
    interestingTypes = []
    for roomType in interpYDataDictionary.keys():
        if IsInterestingType(roomType):
            interestingTypes.append(roomType)
            plt.plot(xDataRawCount, interpYDataDictionary[roomType])
    plt.legend(interestingTypes)
    plt.xticks(ticks=xTicks, labels=xTickLabels, rotation=45)
    plt.xlabel('Time (Date)')
    plt.ylabel('Price (¥)')
    plt.title('Interpolated Price Over Time for Interesting Room Types')
    plt.grid()


    print('Graph 3: Vacancy rates for interesting room types')
    plt.figure()
    vanacies = GetVacanciesPerTick(xTicks, xDataRawCount, yDataDictionary['Village Studio'])
    plt.bar(xTickLabels, vanacies, color='blue')
    plt.xticks(rotation=45)
    # plt.xticks(ticks=xTicks, labels=xTickLabels, rotation=45)
    plt.xlabel('Time (Date)')
    plt.ylabel('Number of Vacant Nights')
    plt.title('Vanacies for Village Studio (Hotel closed: 7-23 May and 11-28 November)')
    plt.grid()

    plt.figure()
    vanacies = GetVacanciesPerTick(xTicks, xDataRawCount, yDataDictionary['Courtyard Studio'])
    plt.bar(xTickLabels, vanacies, color='blue')
    plt.xticks(rotation=45)
    # plt.xticks(ticks=xTicks, labels=xTickLabels, rotation=45)
    plt.xlabel('Time (Date)')
    plt.ylabel('Number of Vacant Nights')
    plt.title('Vanacies for Courtyard Studio (Hotel closed: 7-23 May and 11-28 November)')
    plt.grid()

    print('Graph 4: Average rental rate per tick')
    plt.figure()
    averageRateVillageStudio = GetAverageRatePerTick(xTicks, xDataRawCount, interpYDataDictionary['Village Studio'])
    plt.bar(xTickLabels, averageRateVillageStudio, color='red')
    plt.xticks(rotation=45)
    # plt.xticks(ticks=xTicks, labels=xTickLabels, rotation=45)
    plt.xlabel('Time (Date)')
    plt.ylabel('Average Retal Rate (Yen)')
    plt.title('Average Rental Rate for Village Studio (Hotel closed: 7-23 May and 11-28 November)')
    plt.grid()

    plt.figure()
    averageRate = GetAverageRatePerTick(xTicks, xDataRawCount, interpYDataDictionary['Courtyard Studio'])
    plt.bar(xTickLabels, averageRate, color='red')
    plt.xticks(rotation=45)
    # plt.xticks(ticks=xTicks, labels=xTickLabels, rotation=45)
    plt.xlabel('Time (Date)')
    plt.ylabel('Average Retal Rate (Yen)')
    plt.title('Average Rental Rate for Courtyard Studio (Hotel closed: 7-23 May and 11-28 November)')
    plt.grid()

    print('----------------- OUTPUTTING STATISTICS -----------------')
    for roomType in yDataDictionary.keys():
        # The hotel will be closed from 7-23 May and 11-28 November 2024.
        # This is a total of 17 + 18 = 35 nights
        vacancies = [1 if x is None else 0 for x in yDataDictionary[roomType]]
        print('Room type {0} had {1} nights of vacancies (in addition to normal closures)'.format(roomType, sum(vacancies) - 35))
    print('--------------------------------------------------------')
    for roomType in interpYDataDictionary.keys():
        thisY = interpYDataDictionary[roomType]
        avgPrice = sum(thisY) / len(thisY)
        print('Room type {0} went for, on average {1} yen ({2} USD)'.format(roomType, int(avgPrice), int(avgPrice / 150)))
    print('--------------------------------------------------------')
    print('Tick/average price for Village Studio:')
    for i in range(len(averageRateVillageStudio)):
        print('{0} --- {1} yen'.format(xTickLabels[i], int(averageRateVillageStudio[i])))
    print('--------------------------------------------------------')

    plt.show()



