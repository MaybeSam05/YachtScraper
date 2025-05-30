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
#import psycopg2

load_dotenv()

login_link = os.getenv('login_link')
scrape_link = os.getenv('scrape_link')
username = os.getenv('site_username')
password = os.getenv('site_password')

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

    return driver

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
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table tbody#results tr'))
        )

        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody#results tr')

        new_rows = rows[seen_row_count:]

        for row in new_rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 6:
                    continue

                image_tag = cells[0].find_element(By.TAG_NAME, "img")
                image_url = image_tag.get_attribute("src") if image_tag else ""
                yacht_name = ""
                guests = ""
                length_lines = cells[1].text.strip().splitlines()
                year = cells[2].text.strip()
                specs_lines = [line.strip() for line in cells[3].text.strip().splitlines()]
                agent_lines = cells[4].text.strip().splitlines()
                yacht_id = agent_lines[0].replace("ID:", "").strip() if len(agent_lines) > 0 else ""
                agent_name = agent_lines[1].strip() if len(agent_lines) > 1 else ""
                season_info = cells[5].text.strip()
                length_ft = length_lines[0].replace("ft", "").strip() if len(length_lines) > 0 else ""
                length_m = length_lines[1].replace("m", "").strip() if len(length_lines) > 1 else ""

                for line in specs_lines:
                    if line.lower().startswith("guests"):
                        guests = line.replace("Guests:", "").strip()
                    elif line != "":
                        yacht_name = line

                all_data.append({
                    "yacht_id": yacht_id,
                    "image": image_url,
                    "length_ft": length_ft,
                    "length_m": length_m,
                    "year": year,
                    "yacht_name": yacht_name,
                    "guests": guests,
                    "agent_name": agent_name,
                    "season": season_info,
                })

            except Exception as e:
                print(f"⚠️ Error parsing row: {e}")
                continue

        seen_row_count = len(rows)  

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