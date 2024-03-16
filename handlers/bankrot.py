import asyncio
from service.parse import check_user
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from context.bonkrot import Bankrot

router = Router()


@router.message(Command('bankrot'))
async def set_bankrot(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО")
    await state.set_state(Bankrot.fio)


@router.message(Bankrot.fio)
async def set_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите день/месяц/год рождения\n\n"
                         "в формате 23.05.1983")
    await state.set_state(Bankrot.birthday)


@router.message(Bankrot.birthday)
async def set_birthday(message: types.Message, state: FSMContext):
    await state.update_data(birthday=message.text)
    data = await state.get_data()
    await message.answer("Минуту... \n\n")
    await asyncio.sleep(2)
    check = await check_user(data['fio'], data['birthday'])
    if check:
        await message.answer(f"‼️ {data['fio']} - {data['birthday']}")
    elif check is None:
        await message.answer(f"✅{data['fio']} - {data['birthday']}")
    elif check is False:
        await message.answer(f"👍 {data['fio']} - {data['birthday']}")

