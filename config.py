import os
from dotenv import load_dotenv

from google import genai

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SESSIONS_DIR = "./sessions"

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in environment/.env")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in environment/.env")

os.makedirs(SESSIONS_DIR, exist_ok=True)

client = genai.Client(api_key=GEMINI_API_KEY)
