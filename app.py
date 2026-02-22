import json
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from google import genai


load_dotenv()

gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
gemini_api_key = os.getenv("GEMINI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
SESSIONS_DIR = "./sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

if not gemini_api_key:
    raise RuntimeError("Missing GEMINI_API_KEY in environment/.env")
if not telegram_token:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in environment/.env")


client = genai.Client(api_key=gemini_api_key)

def get_session_path(user_id):
    return os.path.join(SESSIONS_DIR, f"{user_id}.jsonl")

def load_session(user_id):
    """Load conversation history from disk."""
    path = get_session_path(user_id)
    messages = []
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))
    return messages

def append_to_session(user_id, message):
    """Append a single message to the session file."""
    path = get_session_path(user_id)
    with open(path, "a") as f:
        f.write(json.dumps(message) + "\n")

def save_session(user_id, messages):
    """Overwrite the session file with the full message list."""
    path = get_session_path(user_id)
    with open(path, "w") as f:
        for message in messages:
            f.write(json.dumps(message) + "\n")


def to_gemini_contents(messages):
    """Convert stored session messages into google-genai compatible contents."""
    contents = []
    for msg in messages:
        role = msg.get("role", "user")
        # Support both legacy key "content" and the current key "text".
        text = msg.get("text", msg.get("content", ""))
        if not isinstance(text, str):
            text = str(text)
        if not text.strip():
            continue
        contents.append({"role": role, "parts": [{"text": text}]})
    return contents


async def handle_message(update: Update, context):
    user_id = str(update.effective_user.id)
    user_message = update.message.text

      # Load existing conversation
    messages = load_session(user_id)

    # Add new user message
    user_msg = {"role": "user", "text": user_message}
    messages.append(user_msg)
    append_to_session(user_id, user_msg)


    response = client.models.generate_content(
            model=gemini_model,
            contents=to_gemini_contents(messages),
    )

    # Save assistant response
    assistant_msg = {"role": "model", "text": response.text}
    append_to_session(user_id, assistant_msg)
    
    text = response.text
    await update.message.reply_text(text)


app = Application.builder().token(telegram_token).build()
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.run_polling()
