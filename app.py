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
            data={"chat_id": CHAT_ID, "text": text}
        )
    except Exception as e:
        print("Send message error:", e)

# ---------- Scraping Public Notices ----------
def fetch_public_notices():
    """Fetch all Public Notices from NTA JEE Main site"""
    url = "https://jeemain.nta.nic.in/"
    try:
        r = requests.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # Find the Public Notices tab content
        tab_content = soup.find("div", class_="tab-content")
        if not tab_content:
            return "No Public Notices found."

        notices = tab_content.find_all("li")
        if not notices:
            return "No Public Notices found."

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
