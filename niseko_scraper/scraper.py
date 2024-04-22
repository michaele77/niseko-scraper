from matplotlib import pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime
import pickle

# Setup the Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# ------------------------------ #

def OpenBookBar():
    calButton = driver.find_element(By.CLASS_NAME, 'book-bar-guests')
    calButton.click()

def GetDatesForMonth():
    calendarDates = driver.find_elements(By.CSS_SELECTOR, '.month-item .day-item')
    # Ordered array that contains a tuple of {Date text, Data-time}
    # This array can be iterated in order; once the date is no longer decreasing, we can discard this 
    # array and get the one for the next month. 
    orderedDates = []
    for date in calendarDates:
        if 'is-locked' in date.get_attribute('class'):
            print('Skipping date with text {0}'.format(date.text))
            continue
        print('~~~~~~~~~~~~~~~~~~~~~~~ this is the date: ')

        # Print various details about the element
        # print(f"Text: {date.text}")
        # print(f"Tag Name: {date.tag_name}")
        # print(f"Class: {date.get_attribute('class')}")
        # print(f"Date Time!: {date.get_attribute('data-time')}")
        # print(f"ID: {date.get_attribute('id')}")
        # print(f"Is Visible?: {date.is_displayed()}")
        # print(f"Is Enabled?: {date.is_enabled()}")
        # print(f"Size: {date.size}")
        # print(f"Location: {date.location}")
        # print(f"Style: {date.get_attribute('style')}")
        orderedDates.append((int(date.text), date.get_attribute('data-time')))
        time.sleep(.05)
    
    print('This is the map:')
    print(orderedDates)
    return orderedDates

def ClickDateByUnixTime(unixTime):
    day = driver.find_element(By.CSS_SELECTOR, "div[data-time='{0}']".format(unixTime))
    day.click()

def GetStudioRoomElement():
    # Only interested in studio (and maybe one-bedroom)
    # try:
    while True:
        roomResults = driver.find_elements(By.CLASS_NAME, 'result-card')
        if roomResults[0].is_displayed():
            break
        print('Re-fetching...')
        time.sleep(2)
    # except:
    #     print('ERRRORRR <<2>>')
    #     time.sleep(100)
    studioRoom = None
    for room in roomResults:
        # print(f"Text: {room.text}")
        # print(f"Tag Name: {room.tag_name}")
        # print(f"Class: {room.get_attribute('class')}")
        # print(f"ID: {room.get_attribute('id')}")
        # print(f"Is Visible?: {room.is_displayed()}")
        if 'Studio' in room.text:
            studioRoom = room
            # break
    return studioRoom

# Returns true if expansion worked, false if no studios are available at all
def ExpandStudioResult(studioElement):
    # try:
    selectButton = studioElement.find_element(By.CLASS_NAME, 'result-card-select-room-btn')
    # # except:
    # #     print('ERRRRORRRR on <<1>>, waiting....')
    # #     time.sleep(100)
    # if len(selectButton) > 1:
    #     raise AssertionError("There was more than one select button for the studio page")
    # # There should only be one button here
    # for btn in selectButton:
    # print(f"Text: {selectButton.text}")
    # print(f"Tag Name: {selectButton.tag_name}")
    # print(f"Class: {selectButton.get_attribute('class')}")
    # print(f"ID: {selectButton.get_attribute('id')}")
    # print(f"Is Visible?: {selectButton.is_displayed()}")
    # print(f"Is Enabled?: {selectButton.is_enabled()}")
    if not selectButton.is_displayed():
        return False
    selectButton.click()
    time.sleep(1)
    return True

def IsStudioAvailable(studioElement):
    unavailableElements = studioElement.find_elements(By.CLASS_NAME, 'result-card-unavailable')
    print('UNAVAILABLE ELEMENTS: {0}'.format(unavailableElements))
    return len(unavailableElements) == 0

def SwipeToLeft():
    swipable_element = driver.find_elements(By.CSS_SELECTOR, '.swiper-slide.result-choice')
    isNextOne = False
    elementToSwipe = None
    for swipe in swipable_element:
        if isNextOne:
            elementToSwipe = swipe
            break
        if 'swiper-slide-next' in swipe.get_attribute('class'):
            isNextOne = True

    # Create a TouchActions object
    actions = ActionChains(driver)

    # Perform a "drag and hold" action to simulate a scroll
    actions.click_and_hold(elementToSwipe).move_by_offset(-400, 0).perform()  # Move left
    time.sleep(1)  # Add a brief delay for the action to take effect
    # Perform release action to release the mouse button
    actions.release().perform()
    time.sleep(1)

def YenStringToInt(yenString, nightsToStay):
    # Remove non-numeric characters from the string
    numericString = ''.join(char for char in yenString if char.isdigit())
    print('Numeric string: {0}'.format(numericString))
    if not numericString:
        # -1 symbolizes that the unit is not available
        return -1
    return int(numericString) / nightsToStay

def OutputPrices(studioElement, nightsToStay):
    # print('$$$$$$$$$$$$$$$$$$$$$')

    # print(studioElement.text)
    # # print('######################')
    
    typeToPrice = {}
    titles = driver.find_elements(By.CLASS_NAME, 'result-choice-title')
    prices = driver.find_elements(By.CLASS_NAME, 'result-choice-price-label')
    # print('length of title: {0}'.format(len(titles)))
    # print('length of prices: {0}'.format(len(prices)))
    # for i in range(len(titles)):
        # print('title: {0}'.format(titles[i].text))
        # print('prices: {0}'.format(prices[i].text))
    sawNewRoom = True

    while sawNewRoom:
        # print('PRINTING ~~~~~~~~~~~~~~~~ $$$$$')
        roomType = driver.find_elements(By.CLASS_NAME, 'result-choice-body')
        sawNewRoom = False
        for room in roomType:
            title = room.find_element(By.CLASS_NAME, 'result-choice-title')
            price = room.find_element(By.CLASS_NAME, 'result-choice-price-label')
            print('title: {0}'.format(title.text))
            print('prices: {0}'.format(price.text))
            if len(title.text) < 2:
                continue
            if title.text not in typeToPrice:
                
                typeToPrice[title.text] = YenStringToInt(price.text, nightsToStay)
                sawNewRoom = True
                print('<<>> ADDING {0}'.format(title.text))
        # print('PRINTING ~~~~~~~~~~~~~~~~ $$$$$')


        SwipeToLeft()
    return typeToPrice

def GetMonthString():
    thisMonthElement = driver.find_element(By.CSS_SELECTOR, '.month-item.no-previous-month')
    monthString = thisMonthElement.find_element(By.CLASS_NAME, 'month-item-name').text
    print('<<MONTH>> {0}'.format(monthString))
    return monthString

def GetYearString():
    thisMonthElement = driver.find_element(By.CSS_SELECTOR, '.month-item.no-previous-month')
    yearString = thisMonthElement.find_element(By.CLASS_NAME, 'month-item-year').text
    print('<<YEAR>> {0}'.format(yearString))
    return yearString

checkpointCounter = 0

def SaveCheckpointIfNeeded(savePeriodicity, filePath, dataToSave):
    global checkpointCounter
    checkpointCounter += 1
    if checkpointCounter % savePeriodicity != 0:
        print('<<CHECKPOINT>> skipping')
        return
    print('<<CHECKPOINT>> saving, file is {0} long, save time is {1}'.format(len(dataToSave), datetime.now().strftime("%Y_%m_%d-%Hh_%Mm")))
    fullPath = filePath + '.pickle'
    with open(fullPath, 'wb') as file:
        # Serialize and write the map to the file
        pickle.dump(dataToSave, file)


if __name__ == "__main__":
    print('Starting program...')
    nightsToStay = 4
    checkpointEveryNDays = 5
    innerName = datetime.now().strftime("%Y_%m_%d-%Hh_%Mm-stayed_nights_{0}".format(nightsToStay))
    checkpointPath = 'checkpoints/' + innerName
    print('<<CHECKPOINTNAME>> {0}'.format(checkpointPath))
    
    url = 'https://setsuniseko.com/en/book/search'

    # Open the URL
    driver.get(url)
    time.sleep(3)

    OpenBookBar()
    # This is a map of (month string, day int, year string, unix time int) --> {studio type string, price per night int}
    timeTupleToPriceData = {}

    # Will run for a while...top loop is how many months we go through x2.
    # This top loop will loop everytime the month is changed. The months are not interleaved.
    # This means months 1 and 2 will be displayed, then once "next" is clicked, months 3 and 4 will come.
    # HOWEVER, if both dates are on the same month, that month will be "reset" to be the main first month.
    # So then, all we need to do is check that date has not already been scraped and just reset once all dates are collected.
    
    for daysCollected in range(10):
        orderedDates = GetDatesForMonth()
        
        for i, (date, unixTime) in enumerate(orderedDates):
            monthString = GetMonthString()
            yearString = GetYearString()
            tupleKey = (monthString, date, yearString, int(unixTime))
            if tupleKey in timeTupleToPriceData:
                continue

            # Before doing anything else, scroll to the top first.
            driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(0.2)
            # Click on the date range that we want to do
            print('About to click with unix time of {0}'.format(orderedDates[i][1]))
            OpenBookBar()
            time.sleep(0.5)
            ClickDateByUnixTime(orderedDates[i][1])
            time.sleep(0.5)
            print('About to click with unix time of {0}'.format(orderedDates[nightsToStay+i][1]))
            ClickDateByUnixTime(orderedDates[nightsToStay+i][1])
            time.sleep(2)
            
            room = GetStudioRoomElement()
            if not ExpandStudioResult(room):
                print('ROOM IS NOT AVAILABLE! Thats easy....')
                timeTupleToPriceData[tupleKey] = -1
            else:
                # These prices are for the total stay, we need to normalize for per-night.
                pricesPerRoom = OutputPrices(room, nightsToStay)
                print(pricesPerRoom)
                timeTupleToPriceData[tupleKey] = pricesPerRoom
            print('Full map is now: {0}'.format(timeTupleToPriceData))
            SaveCheckpointIfNeeded(checkpointEveryNDays, checkpointPath, timeTupleToPriceData)




    print('DONE!')

    # Close the browser when done
    driver.quit()
