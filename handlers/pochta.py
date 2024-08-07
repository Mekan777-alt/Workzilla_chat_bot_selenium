import os.path

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile

from config import bot
from service.pochta import get_track_info

router = Router()


@router.message(Command('post'))
async def start(message: types.Message):
    await message.answer("Отправьте файл")


@router.message(F.document)
async def handle_document(message: types.Message):

    await message.answer("Ожидайте..")
    await bot.download(
        file=message.document,
        destination=f"{os.getcwd()}\\files\\{message.document.file_name}"
    )

    # get_track_info(message.document.file_name)
    await get_track_info(message.document.file_name, message.from_user.id)
    document = FSInputFile('result.xlsx')
    await bot.send_document(chat_id=message.from_user.id, document=document)
    os.remove('result.xlsx')
    os.remove(f'{os.getcwd()}/files/{message.document.file_name}')
