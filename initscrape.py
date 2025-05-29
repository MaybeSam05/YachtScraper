from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
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
    driver = login()
    data = scrape(driver)

    for index, x in enumerate(data):
        if index < 50:
            print(x)

def backup_login():
    driver = webdriver.Chrome()
    driver.get(login_link)

    time.sleep(30)

    # Manually enter username/password for browser to remember you

    driver.close()

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

    time.sleep(10)

    return driver

def scrape(driver):
    
    driver.get(scrape_link)

    time.sleep(1)

    all_data = []

    seen_row_count = 0

    while True:
        # Wait until there are rows
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table tbody#results tr'))
        )

        # Get all current rows
        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody#results tr')

        # Only process new rows
        new_rows = rows[seen_row_count:]

        for row in new_rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 6:
                    continue

                image_tag = cells[0].find_element(By.TAG_NAME, "img")
                image_url = image_tag.get_attribute("src") if image_tag else ""

                length = cells[1].text.strip()
                year = cells[2].text.strip()
                specs = cells[3].text.strip()
                agent_info = cells[4].text.strip()
                season_info = cells[5].text.strip()

                all_data.append({
                    "image": image_url,
                    "length": length,
                    "year": year,
                    "specs": specs,
                    "agent": agent_info,
                    "season": season_info,
                })

            except Exception as e:
                print(f"⚠️ Error parsing row: {e}")
                continue

        seen_row_count = len(rows)  # update row count tracker

        # Try to click the Load More button
        try:
            load_more_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "load_more_btn"))
            )
            if load_more_btn.is_displayed():
                load_more_btn.click()
                print("🔄 Clicked 'Load More', waiting for new rows...")
                time.sleep(3)
            else:
                break
        except TimeoutException:
            print("✅ No more pages to load.")
            break

    print(f"✅ Finished scraping. Total new rows collected: {len(all_data)}")
    return all_data

if __name__ == "__main__":
    main()