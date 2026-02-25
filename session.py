import json
import os
from config import SESSIONS_DIR

from google.genai import types

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
    """Append a single message (dict or Content) to the session file."""
    if hasattr(message, "to_dict"):
        message = message.to_dict()
    path = get_session_path(user_id)
    with open(path, "a") as f:
        f.write(json.dumps(message) + "\n")

def save_session(user_id, messages):
    """Overwrite the session file with the full message list."""
    path = get_session_path(user_id)
    with open(path, "w") as f:
        for message in messages:
            if hasattr(message, "to_dict"):
                message = message.to_dict()
            f.write(json.dumps(message) + "\n")

def to_gemini_contents(messages):
    """Convert stored session messages into google-genai compatible contents."""
    contents = []
    for msg in messages:
        if isinstance(msg, dict) and "parts" not in msg:
            # Handle legacy format
            role = msg.get("role", "user")
            text = msg.get("text", msg.get("content", ""))
            if text:
                contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
        else:
            # It's already a dict representation of Content or a Content object
            # google-genai handles dicts matching the schema
            contents.append(msg)
    return contents
