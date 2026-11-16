import asyncio
import hashlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from bot import setup_bot
from config import BOT_TOKEN, PORT, PUBLIC_URL
from web import create_app

WEBHOOK_PATH = "/tg-webhook"
WEBHOOK_SECRET = hashlib.sha256(BOT_TOKEN.encode()).hexdigest()[:32]


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    await setup_bot(bot, dp)

    app = create_app()

    if PUBLIC_URL:
        # Webhook rejimi (Render va boshqa hostinglar uchun): Telegram xabari serverni uyg'otadi
        SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
        await bot.set_webhook(
            f"{PUBLIC_URL}{WEBHOOK_PATH}",
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=False,
        )
        logging.info("Webhook: %s%s", PUBLIC_URL, WEBHOOK_PATH)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    logging.info("Web server: http://0.0.0.0:%s", PORT)

    try:
        if PUBLIC_URL:
            await asyncio.Event().wait()  # abadiy ishlash
        else:
            # Lokal sinov: polling
            await bot.delete_webhook(drop_pending_updates=False)
            await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
