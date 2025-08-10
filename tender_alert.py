import requests
from bs4 import BeautifulSoup
import json
import re
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# --- Function to send Telegram alert ---
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

# --- Function to get list of villages in Alipurduar ---
def get_village_list():
    url = "https://villageinfo.in/west-bengal/alipurduar.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    villages = [a.text.strip().lower() for a in soup.select("table a")]
    return set(villages)

# --- Function to scrape tender sites ---
def scrape_site(url, pattern):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ").lower()
        matches = [word for word in village_list if re.search(rf"\b{word}\b", text)]
        if matches:
            send_telegram_message(f"New tender mentioning {', '.join(matches)} found at {url}")
    except Exception as e:
        print(f"Error scraping {url}: {e}")

# --- Main ---
if __name__ == "__main__":
    village_list = get_village_list()

    tender_urls = [
        "https://alipurduar.gov.in/public-utilities/tenders/",
        "https://tenders.gov.in",
        "https://www.asiantender.com",
        "https://westbengal-tenders.in"
    ]

    for site in tender_urls:
        scrape_site(site, village_list)
