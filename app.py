import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# --- Load secrets ---
BOT_TOKEN = st.secrets["BOT_TOKEN"]
CHAT_ID = int(st.secrets["CHAT_ID"])

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

st.title("JEE Update Telegram Bot")
st.write("Bot is active. Send /update in Telegram.")

def send_message(text):
    requests.post(
        f"{API_URL}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True
        },
        timeout=10
    )

def fetch_public_notices():
    url = "https://jeemain.nta.nic.in/"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    section = soup.find("div", id="publicNotice")
    if not section:
        return "No Public Notices found."

    notices = section.find_all("a")
    if not notices:
        return "No Public Notices found."

    out = []
    for n in notices:
        title = n.get_text(strip=True)
        link = n.get("href")
        if link and link.startswith("/"):
            link = "https://jeemain.nta.nic.in" + link
        out.append(f"{title}\n{link}")

    return "\n\n".join(out)

# --- Webhook trigger via query parameter ---
params = st.query_params

if "message" in params:
    try:
        payload = json.loads(params["message"])
        text = payload.get("text", "")

        if text == "/update":
            send_message("Fetching Public Notices ⏳")
            send_message(fetch_public_notices())
    except Exception as e:
        st.error(str(e))

st.success("App running. Waiting for Telegram.")
