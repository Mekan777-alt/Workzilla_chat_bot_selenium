import os

from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command

from config import bot
from service.pochta import get_track_info

router = Router()


@router.message(Command('post'))
async def start(message: types.Message):
    await message.answer("Отправьте файл")


@router.message(F.document)
async def handle_document(message: types.Message):
    # file_path = os.path.join(, message.document.file_name)

    # if document := message.document:
    await bot.download(
        file=message.document,
        destination=f"D:\myProjects\Workzilla_chat_bot_selenium\handlers\\files\\{message.document.file_name}"
    )

    get_track_info(message.document.file_name)
    await bot.send_document(chat_id=message.from_user.id, document=open('result.xlsx', 'rb'))
    # Выведите путь к сохраненному файлу
    print('Успех')
