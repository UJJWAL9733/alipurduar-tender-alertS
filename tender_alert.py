import requests
from bs4 import BeautifulSoup
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
    r = requests.get(url, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")
    villages = [a.text.strip().lower() for a in soup.select("table a")]
    return set(villages)

# --- Function to scrape tender sites ---
def scrape_site(url, village_list):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ").lower()
        matches = [word for word in village_list if re.search(rf"\b{word}\b", text)]
        return matches, True  # (matches, site_checked)
    except requests.exceptions.RequestException:
        return [], False  # site skipped

# --- Main ---
if __name__ == "__main__":
    village_list = get_village_list()

    tender_urls = [
        "https://alipurduar.gov.in/public-utilities/tenders/",
        "https://tenders.gov.in",
        "https://www.asiantender.com",
        "https://westbengal-tenders.in"
    ]

    all_matches = []
    checked_sites = []
    skipped_sites = []

    for site in tender_urls:
        matches, ok = scrape_site(site, village_list)
        if ok:
            checked_sites.append(site)
            if matches:
                send_telegram_message(f"📢 New tender mentioning {', '.join(matches)} found at {site}")
                all_matches.extend(matches)
        else:
            skipped_sites.append(site)

    # Daily summary
    summary = "✅ Daily Check complete.\n"
    if checked_sites:
        summary += f"Checked: {', '.join(checked_sites)}\n"
    if skipped_sites:
        summary += f"Skipped: {', '.join(skipped_sites)}\n"
    if all_matches:
        summary += f"📌 Matches found for: {', '.join(set(all_matches))}"
    else:
        summary += "No new tenders found today."

    send_telegram_message(summary)
