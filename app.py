import asyncio
import logging
from config import dp, bot
from handlers.routers import handler_router


async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(handler_router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())