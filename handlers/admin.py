from aiogram import types, F, Router
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from commands.requests import insert_task
from handlers.keyboards import kb_subject_admin
from models.list_task import subject


admin_router = Router(name='admin_router')


class Task(StatesGroup):
    subject = State()
    number_task = State()
    text = State()
    photo = State()
    answer = State()
    is_hard = State()


@admin_router.message(Command('task'))
async def start_handler(message: Message, l10n: FluentLocalization, state: FSMContext):
    await message.answer(text=l10n.format_value('set-subject'), reply_markup=kb_subject_admin())
    await state.set_state(Task.subject)


@admin_router.callback_query(F.data.startswith('admin_subj'))
async def set_course(callback: CallbackQuery, l10n: FluentLocalization, state: FSMContext):
    subj = callback.data.split(':')[1]
    print(subj)
    await state.update_data(subject=subj)
    await callback.message.answer(text=l10n.format_value('send-number-task'))
    await state.set_state(Task.number_task)


@admin_router.message(F.text, Task.number_task)
async def add_number_task(message: Message, l10n: FluentLocalization, state: FSMContext):
    data = await state.get_data()
    print(data)
    try:
        int(message.text)
        subj = data['subject']
        # Проверка на существование задания
        if subject[subj][1] >= int(message.text) >= subject[subj][0]:
            await state.update_data(number_task=message.text, is_hard=True)
            await state.set_state(Task.photo)
            await message.answer(text=l10n.format_value('send-task'))

        elif int(message.text) < subject[subj][0]:
            await state.update_data(number_task=message.text, is_hard=False)
            await state.set_state(Task.photo)
            await message.answer(text=l10n.format_value('send-task'))
        else:
            await message.answer(text=l10n.format_value('error-not-defined'))
    except ValueError:
        await message.answer(text=l10n.format_value('error-format-number'))


@admin_router.message(F.text, Task.photo)
@admin_router.message(F.photo, Task.photo)
async def add_photo_text(message: Message, l10n: FluentLocalization, state: FSMContext):

    if message.content_type == ContentType.TEXT:
        await state.update_data(text=message.text)
    else:
        await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()

    if data['is_hard'] is False:
        await message.answer(text=l10n.format_value('correct-answer'))
        await state.set_state(Task.answer)
    else:
        if data.get('photo'):
            await insert_task(file_id=data['photo'], user_id=message.from_user.id,
                              number_task=int(data['number_task']), subj=data['subject'])
        else:
            await insert_task(user_id=message.from_user.id, txt=data['text'],
                              number_task=int(data['number_task']), subj=data['subject'])
        await message.answer(text=l10n.format_value('success-send'))
        await state.clear()


@admin_router.message(F.text, Task.answer)
async def add_cur_answer(message: Message, l10n: FluentLocalization, state: FSMContext):
    await state.update_data(answer=message.text)
    data = await state.get_data()

    if data.get('photo'):
        await insert_task(file_id=data['photo'], answer=data['answer'],
                          user_id=message.from_user.id, number_task=int(data['number_task']), subj=data['subject'])
    else:
        await insert_task(user_id=message.from_user.id, txt=data['text'],
                          answer=data['answer'], number_task=int(data['number_task']), subj=data['subject'])
    await message.answer(text=l10n.format_value('success-send'))
    await state.clear()


@admin_router.message(Command("admin"))
async def start_handler(message: Message, l10n: FluentLocalization):
    await message.answer(text='Привет, Админ!')