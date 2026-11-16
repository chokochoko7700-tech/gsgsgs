import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# Serverning ochiq HTTPS manzili. Render buni RENDER_EXTERNAL_URL orqali o'zi beradi.
PUBLIC_URL = (os.getenv("PUBLIC_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
WEBAPP_URL = os.getenv("WEBAPP_URL") or (PUBLIC_URL + "/" if PUBLIC_URL else "")  # mini app manzili
PORT = int(os.getenv("PORT", "8080"))

# Sherlock sozlamalari
SHERLOCK_TIMEOUT = int(os.getenv("SHERLOCK_TIMEOUT", "15"))      # har bir sayt uchun, soniya
MAX_PARALLEL_SEARCHES = int(os.getenv("MAX_PARALLEL_SEARCHES", "2"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. .env faylga yozing.")
