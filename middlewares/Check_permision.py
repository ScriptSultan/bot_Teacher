from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
#
from commands.requests import get_list_teacher, get_list_student
from handlers.admin import admin_router
from handlers.students import student_router
from handlers.teachers import teacher_router
from handlers.users import user_router
from middlewares.config_reader import config


class CheckPermission(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        teacher_list = await get_list_teacher()
        student_list = await get_list_student()
        admin_list = list(map(int, config.admin_chat_id.split(',')))

        if event.chat.id in student_list:
            if data['event_router'].name == student_router.name:
                print(data['event_router'].name)
                return await handler(event, data)
            else:
                print(data['event_router'].name, 'Нет доступа')
                return

        elif event.chat.id in teacher_list:
            if data['event_router'].name == teacher_router.name:
                return await handler(event, data)
            else:
                print(data['event_router'].name, 'Нет доступа')
                return
        elif event.chat.id in admin_list:
            if data['event_router'].name == admin_router.name:
                return await handler(event, data)
            else:
                print(data['event_router'].name, 'Нет доступа')
                return
        else:
            if data['event_router'].name == user_router.name:
                return await handler(event, data)
            else:
                print(data['event_router'].name, 'Нет доступа')
                return
