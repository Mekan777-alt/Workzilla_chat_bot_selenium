import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()

bot = Bot(os.getenv("TOKEN"))

dp = Dispatcher(bot=bot, storage=MemoryStorage())
