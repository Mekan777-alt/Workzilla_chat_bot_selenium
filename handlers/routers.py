from .start import router as start_router
from aiogram import Router
from .bankrot import router as bancrot_router
from .pochta import router as pochta_router


handler_router = Router()


handler_router.include_router(start_router)
handler_router.include_router(bancrot_router)
handler_router.include_router(pochta_router)