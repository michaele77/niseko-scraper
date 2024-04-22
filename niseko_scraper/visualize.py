from matplotlib import pyplot as plt
import pickle

dataFileName = 'checkpoints/2024_04_21-21h_52m-stayed_nights_4.pickle'

def GetData():
    # Open the pickle file in binary read mode
    with open(dataFileName, 'rb') as f:
        # Load the pickled object from the file
        data = pickle.load(f)
    return data

# Returns an array of arrays of price data and an array of string labels.
# Missing data is just set to "None"
def GetArraysForAllStudioTypes(data):
    studioLabels = []
    for someVal in data.values():
        if someVal == -1:
            continue
        studioLabels = someVal.keys()
        break

    dataArrays = {label: [] for label in studioLabels}
    for someVal in data.values():
        for label in studioLabels:
            if not isinstance(someVal, dict):
                dataArrays[label].append(None)
            elif someVal[label] < 0:
                dataArrays[label].append(None)
            else:
                dataArrays[label].append(someVal[label])

    print('Got the denormalized data here: {0}'.format(dataArrays))
    return dataArrays

    

if __name__ == "__main__":
    print('Starting visualization...')

    data = GetData()
    print('See data:')
    print(data)

    print('Graph 1: Print a plot of price per time, excluding times when units are not available')
    # .keys() and .values() return in order of insertion
    xDataUnixTime = [int(i[3]) for i in data.keys()]
    yDataDictionary = GetArraysForAllStudioTypes(data)
    # plt.hold()
    for yData in yDataDictionary.values():
        plt.plot(xDataUnixTime, yData)
    plt.legend(yDataDictionary.keys())
    plt.xlabel('Time (Unix)')
    plt.ylabel('Price (¥)')
    plt.grid()
    plt.show()



