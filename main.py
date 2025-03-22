from playwright.sync_api import sync_playwright
import time

def scrape_yachtworld():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        search_url = "https://www.yachtworld.com/boats-for-sale/"
        page.goto(search_url)
        page.wait_for_timeout(5000) 

        listing_links = page.eval_on_selector_all(
            "a",
            "els => els.map(el => el.href).filter(href => href.includes('/yacht/'))"
        )

        print(f"Found {len(listing_links)} listings")

        for link in listing_links[:5]: 
            print(f"\nScraping: {link}")
            try:
                page.goto(link)
                page.wait_for_timeout(3000)

                title = page.text_content("h1") or "N/A"
                price = page.text_content('[data-testid="price-section-price"]') or "N/A"
                location = page.text_content('[data-testid="detail-location"]') or "N/A"

                print(f"Title: {title.strip()}")
                print(f"Price: {price.strip()}")
                print(f"Location: {location.strip()}")

            except Exception as e:
                print(f"Error scraping {link}: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_yachtworld()
