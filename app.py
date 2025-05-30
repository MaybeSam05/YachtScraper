from flask import Flask, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

login_link = os.getenv('login_link')
scrape_link = os.getenv('scrape_link')
username = os.getenv('site_username')
password = os.getenv('site_password')
db_username = os.getenv('db_username')
db_password = os.getenv('db_password')

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scrape", methods=["GET"])
def trigger_scrape():
    try:
        driver = login()
        data = scrape(driver)
        conn = get_connection()
        save_to_db(data, conn)
        return jsonify({"status": "success", "message": f"{len(data)} rows scraped and saved."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def login():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(
        service=Service("/usr/local/bin/chromedriver"),
        options=chrome_options
    )

    driver.get(login_link)
    time.sleep(1)

    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(username)

    next_button_1 = driver.find_element(By.XPATH, '//button[@data-step="1"]')
    next_button_1.click()
    time.sleep(1)

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
                image_url = image_tag.getAttribute("src") if image_tag else None
                yacht_name = ""
                guests = ""
                length_lines = cells[1].text.strip().splitlines()
                year = cells[2].text.strip()
                specs_lines = [line.strip() for line in cells[3].text.strip().splitlines()]
                agent_lines = cells[4].text.strip().splitlines()
                yacht_id = agent_lines[0].replace("ID:", "").strip()
                agent_name = agent_lines[1].strip() if len(agent_lines) > 1 else None
                season_info = cells[5].text.strip()
                length_ft = length_lines[0].replace("ft", "").strip() if len(length_lines) > 0 else None
                length_m = length_lines[1].replace("m", "").strip() if len(length_lines) > 1 else None

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
                print("🔄 Clicked 'Load More', waiting...")
                time.sleep(3)
            else:
                break
        except TimeoutException:
            print("✅ No more pages to load.")
            break

    print(f"✅ Done. Collected {len(all_data)} rows.")
    return all_data

def get_connection():
    return psycopg2.connect(
        dbname="samarthverma",
        user=db_username,
        password=db_password,
        host="localhost",
        port=5432
    )

def save_to_db(data, conn):
    cursor = conn.cursor()
    for yacht in data:
        cursor.execute(
            """
            INSERT INTO yachtdb (
                yacht_id, image, length_ft, length_m, year, yacht_name, guests, agent_name, season
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (yacht_id) DO UPDATE SET
                image = EXCLUDED.image,
                length_ft = EXCLUDED.length_ft,
                length_m = EXCLUDED.length_m,
                year = EXCLUDED.year,
                yacht_name = EXCLUDED.yacht_name,
                guests = EXCLUDED.guests,
                agent_name = EXCLUDED.agent_name,
                season = EXCLUDED.season;
            """,
            (
                yacht['yacht_id'], yacht['image'], yacht['length_ft'], yacht['length_m'], yacht['year'],
                yacht['yacht_name'], yacht['guests'], yacht['agent_name'], yacht['season']
            )
        )
    conn.commit()
    cursor.close()
    print("✅ Data saved.")

