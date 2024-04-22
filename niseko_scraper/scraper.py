from matplotlib import pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.touch_actions import TouchActions
# from selenium.webdriver import TouchActions
from selenium.webdriver.common.action_chains import ActionChains
import time

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
        print(f"Text: {date.text}")
        print(f"Tag Name: {date.tag_name}")
        print(f"Class: {date.get_attribute('class')}")
        print(f"Date Time!: {date.get_attribute('data-time')}")
        print(f"ID: {date.get_attribute('id')}")
        print(f"Is Visible?: {date.is_displayed()}")
        print(f"Is Enabled?: {date.is_enabled()}")
        print(f"Size: {date.size}")
        print(f"Location: {date.location}")
        print(f"Style: {date.get_attribute('style')}")
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
    roomResults = driver.find_elements(By.CLASS_NAME, 'result-card')
    studioRoom = None
    for room in roomResults:
        print(f"Text: {room.text}")
        print(f"Tag Name: {room.tag_name}")
        print(f"Class: {room.get_attribute('class')}")
        print(f"ID: {room.get_attribute('id')}")
        print(f"Is Visible?: {room.is_displayed()}")
        if 'Studio' in room.text:
            studioRoom = room
            # break
    return studioRoom

def ExpandStudioResult(studioElement):
    selectButton = studioElement.find_elements(By.CLASS_NAME, 'result-card-select-room-btn')
    if len(selectButton) > 1:
        raise AssertionError("There was more than one select button for the studio page")
    # There should only be one button here
    for btn in selectButton:
        print(f"Text: {btn.text}")
        print(f"Tag Name: {btn.tag_name}")
        print(f"Class: {btn.get_attribute('class')}")
        print(f"ID: {btn.get_attribute('id')}")
        print(f"Is Visible?: {btn.is_displayed()}")
        btn.click()
        time.sleep(1)

def OutputPrices(studioElement):
    print('$$$$$$$$$$$$$$$$$$$$$')

    print(studioElement.text)
    print('######################')
    
    typeToPrice = {}
    titles = driver.find_elements(By.CLASS_NAME, 'result-choice-title')
    prices = driver.find_elements(By.CLASS_NAME, 'result-choice-price-label')
    print('length of title: {0}'.format(len(titles)))
    print('length of prices: {0}'.format(len(prices)))
    # for i in range(len(titles)):
        # print('title: {0}'.format(titles[i].text))
        # print('prices: {0}'.format(prices[i].text))
    sawNewRoom = True

    while sawNewRoom:
        print('PRINTING ~~~~~~~~~~~~~~~~ $$$$$')
        roomType = driver.find_elements(By.CLASS_NAME, 'result-choice-body')
        sawNewRoom = False
        for room in roomType:
            title = room.find_element(By.CLASS_NAME, 'result-choice-title')
            price = room.find_element(By.CLASS_NAME, 'result-choice-price-label')
            print('title: {0}'.format(title.text))
            print('prices: {0}'.format(price.text))

            if title not in typeToPrice:
                typeToPrice[title] = price
                sawNewRoom = True
                print('<<>> ADDING {0}'.format(title))
        print('PRINTING ~~~~~~~~~~~~~~~~ $$$$$')

        hasAppendedToOutput = False
        for room in roomType:
            print(f"Text: {room.text}")
            print(f"Tag Name: {room.tag_name}")
            print(f"Class: {room.get_attribute('class')}")
            title = room.find_element(By.CSS_SELECTOR, '.result-choice-title')
            # title = room.find_element(By.CSS_SELECTOR, ".sub-class-name")
            print(f"TITLE Text: {title.text}")
            if title.text in typeToPrice:
                continue
            

            price = room.find_element(By.CSS_SELECTOR, '.result-choice-price-label')
            print(f"TITLE price: {price.text}")
            print(title)
            print(price)
            print('What is length of title?: {0}'.format(title.text))
            if len(title.text) < 2:
                print('SWIPER NO SWIPING!!!')
                # Find the swipable element
                # swipable_element = driver.find_element(By.CSS_SELECTOR, '.result-choice-list .swiper-slide')
                swipable_element = driver.find_elements(By.CSS_SELECTOR, '.swiper-slide.result-choice')
                isNextOne = False
                elementToSwipe = None
                for swipe in swipable_element:
                    if isNextOne:
                        elementToSwipe = swipe
                        break
                    print(f"SWIPE Class: {swipe.get_attribute('class')}")
                    if 'swiper-slide-next' in swipe.get_attribute('class'):
                        isNextOne = True

                # Create a TouchActions object
                # Create an ActionChains object
                actions = ActionChains(driver)

                # Perform a "drag and hold" action to simulate a scroll
                actions.click_and_hold(elementToSwipe).move_by_offset(-400, 0).perform()  # Move left
                time.sleep(1)  # Add a brief delay for the action to take effect
                # Perform release action to release the mouse button
                actions.release().perform()
                time.sleep(1)

                # touch_actions = TouchActions(driver)
                # # Perform the swipe action on the swipable element
                # touch_actions.scroll(swipable_element, -100, 0).perform()  # Swipe left
                # time.sleep(1)  # Add a brief delay for the action to take effect
                # # typeToPrice[]
                time.sleep(1)
                print('RESTARTING LOOP')
                break
            # else:
            #     typeToPrice[title.text] = price.text
            
        # if not hasAppendedToOutput:
        #     sawNewRoom = False
    return typeToPrice


if __name__ == "__main__":
    print('Starting program...')

    url = 'https://setsuniseko.com/en/book/search'

    # Open the URL
    driver.get(url)
    time.sleep(3)


    OpenBookBar()
    orderedDates = GetDatesForMonth()
    
    # while True:
    #     time.sleep(1)
    # Try to click one and two
    # button_1 = driver.find_element(By.CSS_SELECTOR, "div[data-time='{0}']".format(orderedDates[0][1])) #driver.find_elements(By.CSS_SELECTOR, "tagname[data-time='{0}']".format(orderedDates[0][0]))
    # # for b in button_1:
    # print(' 1111    THIS BUTTONNNNNN !!!!!!!!!!!!')
    # print(f"Text: {button_1.text}")
    # print(f"Tag Name: {button_1.tag_name}")
    # print(f"Class: {button_1.get_attribute('class')}")
    # print(f"Date Time!: {button_1.get_attribute('data-time')}")
    #     # print(f"ID: {date.get_attribute('id')}")
    #     # print(f"Is Visible?: {date.is_displayed()}")
    #     # print(f"Is Enabled?: {date.is_enabled()}")
    #     # print(f"Size: {date.size}")
    #     # print(f"Location: {date.location}")
    #     # print(f"Style: {date.get_attribute('style')}")
    # button_1.click()
    # time.sleep(1)
    # # button_2 = driver.find_elements(By.CSS_SELECTOR, "tagname[data-time='{0}']".format(orderedDates[1][0]))
   
    # button_1.click()
    # time.sleep(1)
    # button_2.click()
    # time.sleep(2)
    datesAreIncreasing = True
    prevDate = -1
    nightsToStay = 2
    for i, (date, unixTime) in enumerate(orderedDates):
        # Loop logic.
        if not datesAreIncreasing:
            break
        if prevDate > date:
            datesAreIncreasing = False
        prevDate = date

        # Click on the date range that we want to do
        print('About to click with unix time of {0}'.format(orderedDates[6][1]))
        OpenBookBar()
        time.sleep(0.5)
        ClickDateByUnixTime(orderedDates[6][1])
        time.sleep(0.5)
        print('About to click with unix time of {0}'.format(orderedDates[6+nightsToStay][1]))
        ClickDateByUnixTime(orderedDates[6+nightsToStay][1])
        time.sleep(10)
        
        room = GetStudioRoomElement()
        ExpandStudioResult(room)
        # These prices are for the total stay, we need to normalize for per-night.
        pricesPerRoom = OutputPrices(room)
        print('EXPANDED!')
        time.sleep(2)
        print('WE GOT A PRICE OF: {0}'.format(room.text))




    print('DONE!')

    # Close the browser when done
    driver.quit()
