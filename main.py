import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from bot import setup_bot
from config import BOT_TOKEN, PORT
from web import create_app


async def main():
    logging.basicConfig(level=logging.INFO)

    # 1) Mini app + API server
    runner = web.AppRunner(create_app())
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    logging.info("Web server: http://0.0.0.0:%s", PORT)

    # 2) Telegram bot (polling)
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    await setup_bot(bot, dp)
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
