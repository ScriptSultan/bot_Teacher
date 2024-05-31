import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.admin import admin_router
from handlers.registred import registered_router
from handlers.users import update_filters, user_router
from middlewares.Check_permision import CheckPermission
from middlewares.config_reader import config
from middlewares.fluent_reader import get_fluent_localization
from middlewares.throttling import ThrottlingMiddleware


async def main():
    admin_list = list(map(int, config.admin_chat_id.split(',')))

    logging.basicConfig(
        level=logging.INFO,
        # filename='data/logs.log',
        format="%(asctime)s - %(message)s"
    )

    # Loading localization for bot
    l10n = get_fluent_localization(config.language)

    bot = Bot(token=config.bot_token.get_secret_value())
    # Create Dispatcher
    dp = Dispatcher(storage=MemoryStorage(), l10n=l10n)

    # Add admin filter to admin_router and user_router
    admin_router.message.filter(F.from_user.id.in_(admin_list))
    await update_filters()

    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(registered_router)

    # Registration middleware on throttling
    dp.message.middleware(ThrottlingMiddleware())
    # Registration middleware on router access
    dp.message.middleware(CheckPermission())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
