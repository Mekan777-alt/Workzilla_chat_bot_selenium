from aiogram import types, Router, F
from aiogram.filters import Command
from config import bot

router = Router()


async def set_default_commands(bot):
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить/Перезапустить бота"),
        types.BotCommand(command="bankrot", description="Банкротство"),
        types.BotCommand(command="arbitr", description="Арбитраж"),
        types.BotCommand(command="post", description="Почта"),
    ])


@router.message(Command('start'))
async def start(message: types.Message):
    await set_default_commands(bot)
    await message.answer(f"Дабро пожаловать {message.from_user.first_name}\n\n"
                         f"Выберите команду в списке")
