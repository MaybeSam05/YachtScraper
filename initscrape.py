from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
import time

load_dotenv()

login_link = os.getenv('login_link')
scrape_link = os.getenv('scrape_link')
username = os.getenv('username')
password = os.getenv('password')

def main():
    login()

def login():
    driver = webdriver.Chrome()
    driver.get(login_link)

    time.sleep(1)

    # Enter username
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(username)

    next_button_1 = driver.find_element(By.XPATH, '//button[@data-step="1"]')
    next_button_1.click()

    time.sleep(1)

    # Enter password
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_field.send_keys(password)

    next_button_2 = driver.find_element(By.XPATH, '//button[@data-step="2"]')
    next_button_2.click()

    time.sleep(5)

    driver.close()

def scrape():
    driver = webdriver.Chrome()
    driver.get(scrape_link)

    time.sleep(1)

    driver.close()


if __name__ == "__main__":
    main()