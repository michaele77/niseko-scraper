from matplotlib import pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup the Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# ------------------------------ #


if __name__ == "__main__":
    print('Starting program...')

    # plt.plot([x for x in range(10)], [y*y for y in range(10)])
    # plt.title('Total Assets over Time')
    # plt.xlabel('Age in Years')
    # plt.ylabel('Thousands of Dollars')
    # plt.grid()
    # plt.show()

    url = 'https://setsuniseko.com/en/book/search'

    # Open the URL
    driver.get(url)

    # Wait for the page to load
    time.sleep(3)

    # Open the calendar pop-up by clicking on the date input field
    # date_input = driver.find_element(By.CLASS_NAME, 'date-picker#open')
    allButtons = driver.find_elements(By.XPATH,"//button")
    # date_input.click()
    # for button in allButtons:
    #     print('button: ')
    #     print(button)

    time.sleep(1)
    calButton = driver.find_element(By.CLASS_NAME, 'book-bar-guests')
    calButton.click()

    time.sleep(1)

    # someDates = []
    # someDates.append(driver.find_element(By.XPATH, "//tagname[text()='1']"))
    # someDates.append(driver.find_element(By.XPATH, "//tagname[text()='10']"))
    # someDates.append(driver.find_element(By.XPATH, "//tagname[text()='22']"))
    # someDates.append(driver.find_element(By.XPATH, "//tagname[text()='25']"))
    # for theseDates in someDates:
    #     print(f"Text: {date.text}")
    #     print(f"Tag Name: {date.tag_name}")
    #     print(f"Class: {date.get_attribute('class')}")
    #     print(f"ID: {date.get_attribute('id')}")
    #     print(f"Is Visible?: {date.is_displayed()}")
    #     print(f"Is Enabled?: {date.is_enabled()}")
    #     print(f"Size: {date.size}")
    #     print(f"Location: {date.location}")
    #     print(f"Style: {date.get_attribute('style')}")

    #     if 'is-locked' not in date.get_attribute('class'):
    #         theseDates.click()
    #     time.sleep(.5)


    calendarDates = driver.find_elements(By.CSS_SELECTOR, '.month-item.no-previous-month .day-item')
    # calendarDates = driver.find_elements(By.CLASS_NAME, 'day-item')
    datesToDateData = {}
    for date in calendarDates:
        if 'is-locked' in date.get_attribute('class'):
            print('Skipping date with text {0}'.format(date.text))
            continue
        print('~~~~~~~~~~~~~~~~~~~~~~~ this is the date: ')
        print(date)
        # Get the text content of the div
        text_content = date.text

        # Print the text content if it's not empty
        if text_content.strip():  # Check if text content is not empty or just whitespace
            print(text_content)

        # print(date.)
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
        
        # if int(date.text) > 25:
        
        #     date.click()
        datesToDateData[int(date.text)] = date.get_attribute('data-time')
        
        time.sleep(.2)
    
    print('This is the map:')
    print(datesToDateData)

    print('DONE!')

    # Close the browser when done
    driver.quit()
