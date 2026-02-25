from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from google import genai
from soul import SOUL
from config import GEMINI_MODEL, GEMINI_API_KEY, TELEGRAM_BOT_TOKEN
from tools import run_agent_turn
from session import load_session, save_session, to_gemini_contents


async def handle_message(update: Update, context):
    user_id = str(update.effective_user.id)
    user_message = update.message.text

    # Load existing conversation and convert to Gemini contents
    messages = load_session(user_id)
    contents = to_gemini_contents(messages)

    # Add new user message
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    # Run agent turn (handles tool loop)
    text, updated_contents = run_agent_turn(contents, SOUL)

    # Save full history back to session
    save_session(user_id, updated_contents)
    
    await update.message.reply_text(text)


if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()
