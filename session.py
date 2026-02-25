import json
import os
from config import SESSIONS_DIR

from google.genai import types


def get_session_path(user_id):
    return os.path.join(SESSIONS_DIR, f"{user_id}.jsonl")


def _to_jsonable(value):
    """Recursively normalize SDK objects into plain JSON-serializable data."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}

    for attr in ("to_dict", "model_dump", "dict"):
        fn = getattr(value, attr, None)
        if callable(fn):
            return _to_jsonable(fn())

    if hasattr(value, "__dict__"):
        return _to_jsonable(vars(value))

    return str(value)


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
    message = _to_jsonable(message)
    path = get_session_path(user_id)
    with open(path, "a") as f:
        f.write(json.dumps(message) + "\n")


def save_session(user_id, messages):
    """Overwrite the session file with the full message list."""
    path = get_session_path(user_id)
    with open(path, "w") as f:
        for message in messages:
            message = _to_jsonable(message)
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
