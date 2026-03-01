import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

# Vosk
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "models/vosk-model")

# Trello
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_API_TOKEN = os.getenv("TRELLO_API_TOKEN")
TRELLO_LIST_ID = os.getenv("TRELLO_LIST_ID")

# ffmpeg
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")  # по умолчанию просто "ffmpeg"

# Настройки
TEMP_DIR = os.getenv("TEMP_DIR", "temp")