from aiogram import Router

from handlers.students import student_router
from handlers.teachers import teacher_router


registered_router = Router(name='registered_router')
registered_router.include_routers(student_router, teacher_router)