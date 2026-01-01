import streamlit as st
import requests
import time
from bs4 import BeautifulSoup

# Load Telegram credentials from Streamlit secrets
BOT_TOKEN = st.secrets["BOT_TOKEN"]
CHAT_ID = st.secrets["CHAT_ID"]

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ---------- Telegram helpers ----------
def get_updates(offset=None):
    """Fetch updates from Telegram"""
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=15)
        return r.json()
    except Exception:
        return {"result": []}

def send_message(text):
    """Send message to Telegram group"""
    try:
        requests.post(
            f"{BASE_URL}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        )
    except Exception as e:
        print("Send message error:", e)

# ---------- Scraping Public Notices ----------
def fetch_public_notices():
    """Fetch all Public Notices from NTA JEE Main site"""
    url = "https://jeemain.nta.nic.in/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Find the container div with class containing "gen-list"
        notices_container = soup.find("div", class_=lambda c: c and "gen-list" in c)
        if not notices_container:
            return "No Public Notices found. (Container div not found)"

        # Find the <ul> inside the container
        ul = notices_container.find("ul")
        if not ul:
            return "No Public Notices found. (UL not found)"

        # Find all <li> in the <ul>
        notices = ul.find_all("li")
        if not notices:
            return "No Public Notices found. (No list items)"

        msg = "📢 *JEE Main Public Notices*\n\n"
        for li in notices:
            a_tag = li.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if link.startswith("/"):
                link = "https://jeemain.nta.nic.in" + link
            msg += f"• {title}\n{link}\n\n"

        return msg if msg.strip() else "No Public Notices found."

    except Exception as e:
        return f"Error fetching Public Notices: {e}"

# ---------- Main loop ----------
def main():
    st.write("🤖 Telegram bot running. Waiting for /update …")

    last_update_id = None

    while True:
        updates = get_updates(last_update_id)
        if "result" in updates:
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1

                if "message" in update:
                    text = update["message"].get("text", "")
                    chat_id = str(update["message"]["chat"]["id"])

                    # Only respond to /update command in correct chat
                    if text.strip() == "/update" and chat_id == CHAT_ID:
                        notice_text = fetch_public_notices()
                        send_message(notice_text)

        time.sleep(2)  # Sleep to reduce CPU usage

# ---------- Run ----------
if __name__ == "__main__":
    main()
