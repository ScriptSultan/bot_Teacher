from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from commands.requests import create_profile, get_list_teacher, get_list_student
from handlers.keyboards import setting_role, kb_main_student, kb_subject_teacher, kb_confirm, kb_main_teacher
from handlers.students import student_router
from handlers.teachers import teacher_router
from middlewares.config_reader import config


user_router = Router(name='user_router')


class Form(StatesGroup):
    subject = State()
    name = State()
    link = State()
    student_name = State()
    ref = State()


# Обработка команды start
@user_router.message(Command('start'))
async def start_handler(message: Message, l10n: FluentLocalization):
    affiliate = message.text.split(' ')[1] if message.text != '/start' else None

    await message.answer(text=l10n.format_value('greet'), reply_markup=setting_role(affiliate=affiliate, l10n=l10n))


@user_router.callback_query(F.data.startswith('student'))
async def greet_student(callback: CallbackQuery, l10n: FluentLocalization, state: FSMContext):
    await callback.message.answer(text=l10n.format_value('student-name'))
    ref = callback.data.split('_')[1] if callback.data.split('_')[1] != 'None' else None
    await state.update_data(ref=ref)
    await state.set_state(Form.student_name)


@user_router.message(F.text, Form.student_name)
async def greet_student(message: Message, l10n: FluentLocalization, state: FSMContext):
    data = await state.get_data()

    await create_profile(user_id=message.from_user.id, fullname=message.from_user.full_name,
                         username=message.from_user.username, is_teacher=False, ref=data['ref'],
                         student_name=message.text)
    await message.answer(text=l10n.format_value('greet-student'),
                         reply_markup=kb_main_student(ref_id=data['ref'], l10n=l10n))
    # Обновление фильтров для роутеров
    await update_filters()


@user_router.callback_query(F.data == 'teacher')
async def choice_subject(callback: CallbackQuery, l10n: FluentLocalization, state: FSMContext):
    await callback.message.answer(l10n.format_value('choose-subject'), reply_markup=kb_subject_teacher())
    await callback.answer()


@user_router.callback_query(F.data.startswith('subj'))
async def get_subject(callback: CallbackQuery, l10n: FluentLocalization, state: FSMContext):
    await state.update_data(subject=callback.data.split(':')[1])
    await state.set_state(Form.name)
    await callback.message.answer(text=l10n.format_value('get-teacher-name'))
    await callback.answer()


@user_router.message(F.text, Form.name)
async def send_name(message: Message, l10n: FluentLocalization, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.link)
    await message.answer(text=l10n.format_value('get-teacher-link'))


@user_router.message(F.text, Form.link)
async def send_request(message: Message, l10n: FluentLocalization, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    await message.bot.send_message(chat_id=312390617,
                                   text=f'{data["name"]} - {data["subject"]} - {data["link"]}',
                                   reply_markup=kb_confirm(user_id=message.from_user.id,
                                                           username=message.from_user.username,
                                                           fullname=message.from_user.full_name,
                                                           l10n=l10n),
                                   disable_web_page_preview=True)
    await state.clear()


@user_router.callback_query(F.data.startswith('confirm'))
async def get_check(callback: CallbackQuery, l10n: FluentLocalization):
    data = callback.data.split(':')
    msg = callback.message.text.split('-')
    await create_profile(user_id=int(data[1]), username=data[2], fullname=data[3],
                         is_teacher=True, teacher_name=msg[0], link=msg[2], subj=msg[1])
    await callback.bot.send_message(chat_id=int(data[1]),
                                    text=l10n.format_value('success-register-teacher'))

    await callback.bot.send_message(chat_id=int(data[1]),
                                    text=l10n.format_value('main-menu'),
                                    reply_markup=kb_main_teacher(l10n=l10n))
    await callback.message.delete()

    # Обновление фильтров для роутеров
    await update_filters()
    await callback.answer()


@user_router.callback_query(F.data == 'delete')
async def cancel_request(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.message.delete()
    await callback.answer()


async def update_filters():
    teacher_list = await get_list_teacher()
    student_list = await get_list_student()
    admin_list = list(map(int, config.admin_chat_id.split(',')))

    user_router.message.filter(~F.from_user.id.in_(teacher_list + student_list + admin_list))
    student_router.message.filter(~F.from_user.id.in_(teacher_list + admin_list))
    teacher_router.message.filter(~F.from_user.id.in_(student_list + admin_list))

    print(f'{teacher_list=}\n{student_list=}')
    print('Filters is updated')


@user_router.message(Command("user"))
async def start_handler(message: Message, l10n: FluentLocalization):
    await message.answer(text='Привет, Незнакомец!')