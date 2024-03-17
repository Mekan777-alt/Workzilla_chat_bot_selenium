import os
import asyncio
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from context.arbitr import ArbitrState
from service.arbitr_service import check_table, list_image
from service.zip_file import zip_files
from config import bot
from aiogram.types import FSInputFile

router = Router()


@router.message(Command('arbitr'))
async def send_arbitr(message: types.Message, state: FSMContext):
    await message.answer("Введите список")
    await state.set_state(ArbitrState.fio)


@router.message(ArbitrState.fio)
async def fio_set(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    data = await state.get_data()
    await message.answer("Минуту...")
    text = ""
    value_list = data['fio'].split('\n')
    for value in value_list:
        check = check_table(value)
        await asyncio.sleep(120)
        if check:
            text += f"‼️ {value}\n"
        elif check is False:
            text += f"✅ {value}\n"
        elif check is None:
            text += f"Произошла ошибка по запросу {value}!!!\n"

    file_image = zip_files(list_image)
    path_file = FSInputFile(file_image)

    await message.answer(text)
    await bot.send_document(message.from_user.id, document=path_file)
    await state.clear()
    os.remove(path_file.path)
    for value in list_image:
        os.remove(value)
    list_image.clear()

