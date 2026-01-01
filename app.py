import streamlit as st
import asyncio
from telegram.ext import Application, CommandHandler

# Load secrets from Streamlit
BOT_TOKEN = st.secrets["BOT_TOKEN"]

async def update_cmd(update, context):
    await update.message.reply_text("Bot is alive ✅")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Register /update command
    app.add_handler(CommandHandler("update", update_cmd))

    # Start bot
    await app.initialize()
    await app.start()

    # Keep app running forever
    await asyncio.Event().wait()

# Streamlit needs this guard
if __name__ == "__main__":
    asyncio.run(main())
