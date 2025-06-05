# Yacht Scraper

Web application that automates the process of scraping yacht information from the MLS website and storing it in a Supabase database.

## Features

- Automated login and data scraping
- Extracts yacht details including:
  - Yacht ID
  - Images
  - Length (ft/m)
  - Year
  - Yacht name
  - Guest capacity
  - Agent information
  - Season availability
  - PDF brochures
- Web interface for easy operation
- Supabase database integration

## Prerequisites

1. Python 3.7+
2. Chrome browser
3. Supabase account and database
4. Required Python packages (install via `pip install -r requirements.txt`):
   - Flask
   - selenium
   - psycopg2
   - python-dotenv

## Setup

1. Clone this repository
2. Create a `.env` file in the root directory with the following variables:

```
login_link=YOUR_LOGIN_URL
scrape_link=YOUR_SCRAPE_URL
site_username=YOUR_SITE_USERNAME
site_password=YOUR_SITE_PASSWORD
SUPABASE_HOST=YOUR_SUPABASE_HOST
SUPABASE_DB_PASSWORD=YOUR_DB_PASSWORD
SUPABASE_DB_USER=YOUR_DB_USER
SUPABASE_DB_NAME=YOUR_DB_NAME
SUPABASE_DB_PORT=5432
```

## Usage

1. Start the Flask application:

```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. **Important**: Click "Initial Login (Run this First)" button (One Time Setup)

   - This opens a Chrome window
   - Wait for the login page to load
   - The browser will remember your login session for subsequent scraping

4. Once logged in, click "Run Scraper" to start the data collection

   - The scraper will automatically:
     - Navigate through pages
     - Extract yacht information
     - Download PDF brochures
     - Save data to Supabase

5. Monitor the status in the web interface
   - Success/error messages will be displayed
   - Check the browser console for detailed logs

## Database Schema

The `yachtdb` table in Supabase contains the following columns:

- `yacht_id` (primary key)
- `image` (URL)
- `length_ft` (numeric)
- `length_m` (numeric)
- `year` (integer)
- `yacht_name` (text)
- `guests` (text)
- `agent_name` (text)
- `season` (text)
- `pdf_url` (text)

## Troubleshooting

1. **Login Issues**

   - Use the "Initial Login" button to manually log in
   - Check your `.env` credentials
   - Ensure your account has necessary permissions

2. **Scraping Problems**

   - Check Chrome version compatibility
   - Verify network connectivity
   - Look for error messages in the console

3. **Database Connection**
   - Verify Supabase credentials
   - Check database permissions
   - Ensure proper network access to Supabase
