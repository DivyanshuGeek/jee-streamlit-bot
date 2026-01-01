import streamlit as st
import requests
import time
from bs4 import BeautifulSoup

BOT_TOKEN = st.secrets["BOT_TOKEN"]
CHAT_ID = st.secrets["CHAT_ID"]

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None):
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset
    return requests.get(f"{BASE_URL}/getUpdates", params=params).json()

def send_message(text):
    requests.post(
        f"{BASE_URL}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )

def fetch_public_notices():
    url = "https://jeemain.nta.nic.in/"
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    notices = soup.select("div.public-notice a")
    if not notices:
        return "No Public Notices found."

    msg = "📢 *JEE Main Public Notices*\n\n"
    for a in notices:
        title = a.get_text(strip=True)
        link = a.get("href")
        if link and not link.startswith("http"):
            link = url + link
        msg += f"• {title}\n{link}\n\n"

    return msg

def main():
    st.write("🤖 Bot running. Waiting for /update …")

    last_update_id = None

    while True:
        updates = get_updates(last_update_id)
        if "result" in updates:
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1

                if "message" in update:
                    text = update["message"].get("text", "")
                    chat_id = str(update["message"]["chat"]["id"])

                    if text.strip() == "/update" and chat_id == CHAT_ID:
                        notice_text = fetch_public_notices()
                        send_message(notice_text)

        time.sleep(2)

if __name__ == "__main__":
    main()
