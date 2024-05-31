from aiogram import types, F, Router
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from commands.requests import insert_task, get_list_student_for_teacher, get_statistic_person, get_homework_false, \
    get_hardtask, complete_homework
from handlers.keyboards import kb_main_teacher, kb_person, kb_next_static, kb_get_hardtask
from models.list_task import subject


teacher_router = Router(name='teacher_router')


class Task(StatesGroup):
    #добавить предмет
    number_task = State()
    text = State()
    photo = State()
    answer = State()
    is_hard = State()


# Обработка команды start
@teacher_router.message(Command("start"))
async def start_handler(message: Message, l10n: FluentLocalization):
    await message.answer(text=l10n.format_value('main-menu'), reply_markup=kb_main_teacher(l10n=l10n))


@teacher_router.callback_query(F.data == 'add_exercise')
async def add_tasks(callback: CallbackQuery, l10n: FluentLocalization, state: FSMContext):
    await state.set_state(Task.number_task)
    await callback.message.answer(text=l10n.format_value('send-number-task'))
    await callback.answer()


@teacher_router.message(F.text, Task.number_task)
async def add_number_task(message: Message, l10n: FluentLocalization, state: FSMContext):

    try:
        int(message.text)
        subj = await get_ref_subj(user_id=message.from_user.id)
        # Проверка на существование задания
        if subject[subj[1]][1] >= int(message.text) >= subject[subj[1]][0]:
            await state.update_data(number_task=message.text, is_hard=True)
            await state.set_state(Task.photo)
            await message.answer(text=l10n.format_value('send-task'))

        elif int(message.text) < subject[subj[1]][0]:
            await state.update_data(number_task=message.text, is_hard=False)
            await state.set_state(Task.photo)
            await message.answer(text=l10n.format_value('send-task'))
        else:
            await message.answer(text=l10n.format_value('error-not-defined'))
    except ValueError:
        await message.answer(text=l10n.format_value('error-format-number'))


@teacher_router.message(F.text, Task.photo)
@teacher_router.message(F.photo, Task.photo)
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
            await insert_task(file_id=data['photo'],
                              user_id=message.from_user.id, number_task=int(data['number_task']))
        else:
            await insert_task(user_id=message.from_user.id, txt=data['text'], number_task=int(data['number_task']))
        await message.answer(text=l10n.format_value('success-send'))
        await state.clear()


@teacher_router.message(F.text, Task.answer)
async def add_cur_answer(message: Message, l10n: FluentLocalization, state: FSMContext):
    await state.update_data(answer=message.text)
    data = await state.get_data()

    if data.get('photo'):
        await insert_task(file_id=data['photo'], answer=data['answer'],
                          user_id=message.from_user.id, number_task=int(data['number_task']))
    else:
        await insert_task(user_id=message.from_user.id, txt=data['text'],
                          answer=data['answer'], number_task=int(data['number_task']))
    await message.answer(text=l10n.format_value('success-send'))
    await state.clear()


@teacher_router.callback_query(F.data == 'list_student')
async def list_of_stud(callback: CallbackQuery, l10n: FluentLocalization):
    list_student = await get_list_student_for_teacher(user_id=callback.from_user.id)
    if not list_student:
        await callback.message.answer(text='Список учеников пуст')
    else:
        await callback.message.answer(text=l10n.format_value('list-student'), reply_markup=kb_list_students(list_student=list_student))
    await callback.answer()


@teacher_router.callback_query(F.data.startswith('person:'))
async def get_person(callback: CallbackQuery, l10n: FluentLocalization):
    data = callback.data.split(':')
    await callback.message.answer(text=l10n.format_value(msg_id='statistic', args={'name': data[1]}),
                                  reply_markup=kb_person(data[1], data[2], l10n=l10n))
    await callback.answer()


@teacher_router.callback_query(F.data.startswith('statistic:'))
async def get_statistic(callback: CallbackQuery, l10n: FluentLocalization):
    data = callback.data.split(':')
    statistic = await get_statistic_person(user_id=int(data[2]))
    await callback.message.answer(text=l10n.format_value(msg_id='statistic', args={'name': data[1],
                                                                                   'complete': statistic[0],
                                                                                   'not_checked': statistic[1],
                                                                                   'not_complete': statistic[2]}),
                                  reply_markup=kb_next_static(user_id=data[2], l10n=l10n))
    await callback.answer()


@teacher_router.callback_query(F.data.startswith('homework'))
async def check_homework(callback: CallbackQuery, l10n: FluentLocalization):
    user_id = callback.data.split(':')[1]
    homeworks = await get_homework_false(int(user_id))

    for work in homeworks:
        try:
            await callback.message.answer_photo(photo=work[1],
                                                reply_markup=kb_get_hardtask(hardtask_id=work[0], user_id=user_id, l10n=l10n))
        except TelegramBadRequest:
            await callback.message.answer(text=work[1],
                                          reply_markup=kb_get_hardtask(hardtask_id=work[0], user_id=user_id, l10n=l10n))
    else:
        await callback.message.answer(text=l10n.format_value('no-homework'))
    await callback.answer()


@teacher_router.callback_query(F.data.startswith('get_hardtask:'))
async def show_hardtask_for_teacher(callback: CallbackQuery, l10n: FluentLocalization):
    hardtask_id = int(callback.data.split(':')[1])
    hardtask = await get_hardtask(hardtask_id=hardtask_id)

    if hardtask[0] is None:
        print(hardtask[0])
        await callback.message.answer(text=hardtask[1])
    else:
        await callback.message.answer_photo(photo=hardtask[0])
    await callback.answer()


@teacher_router.callback_query(F.data.startswith('cancel'))
@teacher_router.callback_query(F.data.startswith('complete'))
async def complete_homework_hardtask(callback: CallbackQuery, l10n: FluentLocalization):
    data = callback.data.split(":")
    if data[0] == 'complete':
        await complete_homework(hardtask_id=int(data[1]), user_id=int(data[2]))
        await callback.bot.send_message(chat_id=int(data[2]),
                                        text=l10n.format_value('success-homework'))
    elif data[0] == 'cancel':
        await cancel_homework(hardtask_id=int(data[1]), user_id=int(data[2]))
        await callback.bot.send_message(chat_id=int(data[2]),
                                        text=l10n.format_value('homework_mistake'))
    await callback.answer()



@teacher_router.message(Command("teacher"))
async def start_handler(message: Message, l10n: FluentLocalization):
    await message.answer(text='Привет, Учитель!')