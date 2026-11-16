import html
import time

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
)

import sherlock_runner
from config import WEBAPP_URL

router = Router()


def _webapp_kb() -> InlineKeyboardMarkup | None:
    if not WEBAPP_URL:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔎 Mini app'ni ochish", web_app=WebAppInfo(url=WEBAPP_URL))]]
    )


@router.message(CommandStart())
async def start(msg: Message):
    await msg.answer(
        "👋 Salom! Bu bot username bo'yicha 400+ saytdan ochiq profillarni qidiradi "
        "(<a href='https://github.com/sherlock-project/sherlock'>Sherlock</a> asosida).\n\n"
        "• Mini app orqali qidiring, yoki\n"
        "• Chatga yozing: <code>/search username</code>",
        reply_markup=_webapp_kb(),
        disable_web_page_preview=True,
    )


@router.message(Command("search"))
async def search_cmd(msg: Message, command: CommandObject):
    username = (command.args or "").strip().lstrip("@")
    await run_search(msg, username)


@router.message(F.text & ~F.text.startswith("/"))
async def plain_text(msg: Message):
    await run_search(msg, msg.text.strip().lstrip("@"))


async def run_search(msg: Message, username: str):
    if not sherlock_runner.is_valid_username(username):
        await msg.answer("❗ Username yuboring. Masalan: <code>/search johndoe</code>\n"
                         "Faqat harf, raqam, <code>. _ -</code> (2–40 belgi).")
        return

    status = await msg.answer(f"⏳ <b>{html.escape(username)}</b> qidirilmoqda… (1–3 daqiqa)")
    found: list[dict] = []
    last_edit = 0.0
    try:
        async for item in sherlock_runner.search(username, msg.from_user.id):
            found.append(item)
            if time.monotonic() - last_edit > 3:  # Telegram limitlariga tushmaslik uchun
                last_edit = time.monotonic()
                await status.edit_text(f"⏳ <b>{html.escape(username)}</b> — hozircha {len(found)} ta topildi…")
    except sherlock_runner.SearchBusy:
        await status.edit_text("⏳ Oldingi qidiruvingiz hali tugamadi, kuting.")
        return
    except Exception as e:  # noqa: BLE001
        await status.edit_text(f"⚠️ Xatolik: {html.escape(str(e))}")
        return

    if not found:
        await status.edit_text(f"🤷 <b>{html.escape(username)}</b> bo'yicha hech narsa topilmadi.")
        return

    await status.edit_text(f"✅ <b>{html.escape(username)}</b> — {len(found)} ta profil topildi:")
    lines = [f"• <a href='{html.escape(r['url'])}'>{html.escape(r['site'])}</a>" for r in found]
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) > 3800:
            await msg.answer(chunk, disable_web_page_preview=True)
            chunk = ""
        chunk += line + "\n"
    if chunk:
        await msg.answer(chunk, disable_web_page_preview=True)


async def setup_bot(bot: Bot, dp: Dispatcher):
    dp.include_router(router)
    if WEBAPP_URL:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Qidiruv", web_app=WebAppInfo(url=WEBAPP_URL))
        )
