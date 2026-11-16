import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")  # https://... (mini app manzili)
PORT = int(os.getenv("PORT", "8080"))

# Sherlock sozlamalari
SHERLOCK_TIMEOUT = int(os.getenv("SHERLOCK_TIMEOUT", "15"))      # har bir sayt uchun, soniya
MAX_PARALLEL_SEARCHES = int(os.getenv("MAX_PARALLEL_SEARCHES", "2"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. .env faylga yozing.")
