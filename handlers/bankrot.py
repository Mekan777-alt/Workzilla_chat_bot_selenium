import asyncio
from service.parse import check_user
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from context.bonkrot import Bankrot
from service.zip_file import zip_files
from service.parse import image_file_list
from config import bot
import os
from aiogram.types import FSInputFile

router = Router()


@router.message(Command('bankrot'))
async def set_bankrot(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО")
    await state.set_state(Bankrot.fio)


@router.message(Bankrot.fio)
async def set_birthday(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    data = await state.get_data()
    await message.answer("Минуту... \n\n")
    value_list = data['fio'].split('\n')
    text = ""
    for value in value_list:
        try:
            fio, birthday = value.split(' - ')
            check = await check_user(fio, birthday)

            await asyncio.sleep(10)
            if check:
                text += f"‼️ {fio} - {birthday}\n"
            elif check is None:
                text += f"✅{fio} - {birthday}\n"
            elif check is False:
                text += f"👍 {fio} - {birthday}\n"
        except ValueError:
            await message.answer("Введины не валидные данные\n\n"
                                 "Повторите")
            await state.clear()
    file = zip_files(image_file_list)
    path_file = FSInputFile(file)
    await state.clear()
    await message.answer(text)
    await bot.send_document(message.from_user.id, document=path_file)
    await asyncio.sleep(5)
    os.remove(path_file.path)
    for value in image_file_list:
        os.remove(value)
    image_file_list.clear()
