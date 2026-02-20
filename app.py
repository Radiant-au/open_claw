import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

load_dotenv()

gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
gemini_api_key = os.getenv("GEMINI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

if not gemini_api_key:
    raise RuntimeError("Missing GEMINI_API_KEY in environment/.env")
if not telegram_token:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in environment/.env")

use_new_sdk = True
try:
    from google import genai
except ImportError:
    import google.generativeai as genai
    use_new_sdk = False

if use_new_sdk:
    client = genai.Client(api_key=gemini_api_key)
else:
    genai.configure(api_key=gemini_api_key)
    legacy_model = genai.GenerativeModel(gemini_model)


async def handle_message(update: Update, context):
    user_message = update.message.text
    if use_new_sdk:
        response = client.models.generate_content(
            model=gemini_model,
            contents=user_message,
        )
        text = response.text
    else:
        response = legacy_model.generate_content(user_message)
        text = response.text

    await update.message.reply_text(text)


app = Application.builder().token(telegram_token).build()
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.run_polling()
