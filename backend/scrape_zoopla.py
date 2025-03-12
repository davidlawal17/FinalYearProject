import time
import os
import psycopg2
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")


def connect_db():
    """Establishes connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        print("❌ Database connection failed:", str(e))
        return None


def setup_selenium():
    """Initializes undetected Selenium WebDriver."""
    options = uc.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    return driver


def scrape_zoopla():
    """Scrapes property listings from Zoopla using undetected Selenium."""
    ZOOPLA_URL = "https://www.zoopla.co.uk/for-sale/property/london/?price_max=500000&beds_min=2"

    print("🚀 Launching undetected Selenium WebDriver...")
    driver = setup_selenium()
    driver.get(ZOOPLA_URL)

    # Wait until property listings are visible
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-1itfubx"))  # Update class if changed
        )
    except:
        print("⚠️ Property listings did not load.")
        driver.quit()
        return []

    # Scroll down multiple times to load more properties
    for _ in range(5):  # Increase scroll count
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

    # Extract page source and close driver
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    print("🔍 Extracting property data...")
    properties = soup.find_all('div', class_='css-1itfubx')  # Update class if needed

    if not properties:
        print("⚠️ No properties found. Check HTML structure.")
        return []

    scraped_data = []
    for property in properties:
        try:
            title = property.find('h2', class_='css-b2lm5p').text.strip()
            price = property.find('p', class_='css-18tf9v5').text.strip()
            location = property.find('p', class_='css-1p8grtv').text.strip()
            url = "https://www.zoopla.co.uk" + property.find('a', class_='css-1wnihdy')['href']

            scraped_data.append((title, price, location, url))
        except AttributeError:
            continue  # Skip if data is missing

    print(f"✅ Scraped {len(scraped_data)} properties.")
    return scraped_data


def store_data_in_db(data):
    """Stores scraped property data in PostgreSQL."""
    conn = connect_db()
    if not conn:
        return

    cur = conn.cursor()

    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price TEXT,
            location TEXT,
            url TEXT
        )
    """)

    # Insert new data
    cur.executemany("INSERT INTO properties (title, price, location, url) VALUES (%s, %s, %s, %s)", data)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Data successfully stored in the database.")


def main():
    """Main function to scrape and store property data."""
    data = scrape_zoopla()
    if data:
        store_data_in_db(data)
        print("✅ Scraping & storage completed.")
    else:
        print("⚠️ No data scraped. Please check your Zoopla request.")


if __name__ == "__main__":
    main()
