from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from commands.requests import get_subj_ref_from_student, update_subj_student, get_task, insert_homework, \
    get_subj_from_teacher, get_list_homework, get_task_by_id
from handlers.keyboards import kb_main_student, kb_subj_student, kb_tasks, kb_set_answer, kb_task_again, kb_list_tasks


student_router = Router(name='student_router')


class Answer(StatesGroup):
    id_task = State()
    is_hard = State()
    answer = State()
    solved = State()
    task_answer = State()
    subject = State()


# Обработка команды start
@student_router.message(Command("start"))
async def start_handler(message: Message, l10n: FluentLocalization):
    subj = await get_subj_ref_from_student(user_id=message.from_user.id)
    await message.answer(text=l10n.format_value('main-menu'),
                         reply_markup=kb_main_student(subj=subj[0], ref_id=subj[1], l10n=l10n))


@student_router.callback_query(F.data == 'set_course')
async def set_course(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.message.edit_text(text=l10n.format_value('choose-student-subject'),
                                     reply_markup=kb_subj_student())
    await callback.answer()


@student_router.callback_query(F.data.startswith('stud_subj'))
async def set_subj(callback: CallbackQuery, l10n: FluentLocalization):
    subj = callback.data.split(':')[1]
    await update_subj_student(user_id=callback.from_user.id, subj=subj)
    await callback.message.edit_text(text=l10n.format_value('main-menu'),
                                     reply_markup=kb_main_student(subj=subj, ref_id=subj[1], l10n=l10n))
    await callback.answer()


@student_router.callback_query(F.data == 'first_tasks')
@student_router.callback_query(F.data == 'hard_task')
async def choose_task(callback: CallbackQuery, l10n: FluentLocalization):
    subj = await get_subj_ref_from_student(callback.from_user.id)
    if subj[0] is None:
        await callback.message.edit_text(text=l10n.format_value('choose-student-subject'))
    else:
        await callback.message.edit_text(text=l10n.format_value('choose-number-task'),
                                         reply_markup=kb_tasks(subj[0], callback_data=callback.data, l10n=l10n))
    await callback.answer()


@student_router.callback_query(F.data == 'back_main')
async def back_handler(callback: CallbackQuery, l10n: FluentLocalization):
    subj = await get_subj_ref_from_student(callback.from_user.id)
    await callback.message.edit_text(text=l10n.format_value('main-menu'),
                                     reply_markup=kb_main_student(subj=subj[0], ref_id=subj[1], l10n=l10n))
    await callback.answer()


@student_router.callback_query(F.data.startswith('task'))
async def get_chosen_task(callback: CallbackQuery, l10n: FluentLocalization, state: FSMContext):
    data = callback.data.split(':')
    is_hard = False if data[1] == 'first' else True
    await state.update_data(subject=data[2])
    task = await get_task(number_task=data[3], is_hard=is_hard, subj=data[2])
    if is_hard is False:
        await state.update_data(solved=str(task[2]))
    if task is None:
        await callback.message.answer(text=l10n.format_value('error-no-tasks'))
    else:
        if task[1] is None:
            await callback.message.answer_photo(photo=task[0])
            await callback.message.answer(text=l10n.format_value('send-answer'),
                                          reply_markup=kb_set_answer(l10n=l10n, is_hard=is_hard, task_id=int(data[3])))
        else:
            await callback.message.answer(text=task[1])
            await callback.message.answer(text=l10n.format_value('send-answer'),
                                          reply_markup=kb_set_answer(l10n=l10n, is_hard=is_hard, task_id=int(data[3])))
    await callback.answer()


@student_router.callback_query(F.data.startswith('check-answer'))
async def set_answer(callback: CallbackQuery, l10n: FluentLocalization, state: FSMContext):
    data = callback.data.split(':')

    is_hard = False if data[1] == 'task' else True
    await state.update_data(id_task=data[2], is_hard=is_hard)

    await callback.message.answer(text=l10n.format_value('set-answer-student'))
    await state.set_state(Answer.task_answer)
    await callback.answer()


@student_router.message(F.text, Answer.task_answer)
async def get_answer(message: Message, l10n: FluentLocalization, state: FSMContext):
    await state.update_data(task_answer=message.text)
    data = await state.get_data()

    if data['is_hard'] is True:
        await message.answer(text=l10n.format_value('send-homework'),
                             reply_markup=kb_task_again(l10n=l10n, subj=data['subject'], is_hard=True))
        await insert_homework(user_id=message.from_user.id, task_id=data['id_task'],
                              is_hard=True, answer=data['task_answer'])
        await state.clear()
    else:
        print(data)
        if data['task_answer'] == data['solved']:
            await message.answer(text=l10n.format_value('correct'),
                                 reply_markup=kb_task_again(l10n=l10n, subj=data['subject'], is_hard=False))
            await state.clear()
        else:
            await message.answer(text=l10n.format_value('incorrect'))


@student_router.callback_query(F.data == 'kim')
async def get_kim(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.message.answer(text='В разработке')
    await callback.answer()


@student_router.callback_query(F.data == 'work_teacher')
async def homework_handler(callback: CallbackQuery, l10n: FluentLocalization):
    subj = await get_subj_from_teacher(callback.from_user.id)
    task_list = await get_list_homework(user_id=callback.from_user.id)

    await callback.message.edit_text(text=l10n.format_value('list-homework'),
                                     reply_markup=kb_list_tasks(list_task=task_list, subj=subj, l10n=l10n))
    await callback.answer()


@student_router.callback_query(F.data.startswith('taperson'))
async def get_hm_tasks(callback: CallbackQuery, l10n: FluentLocalization, state: FSMContext):
    data = callback.data.split(':')
    if data[1] == 'task':
        task = await get_task_by_id(user_id=callback.from_user.id, is_hard=False, task_id=data[2])
        await state.update_data(is_hard=False, id_task=data[2], solved=str(task[3]))
    else:
        await state.update_data(is_hard=True, id_task=data[2])
        task = await get_task_by_id(user_id=callback.from_user.id, is_hard=True, task_id=data[2])
    if task[1] is None:
        await callback.message.edit_text(text=task[2])
    else:
        await callback.message.delete()
        await callback.message.answer_photo(photo=task[1])
    await callback.message.answer(text=l10n.format_value('set-answer'))
    await state.set_state(Answer.answer)
    await callback.answer()


@student_router.message(F.text, Answer.answer)
async def check_handler(message: Message, l10n: FluentLocalization, state: FSMContext):
    await state.update_data(answer=message.text)
    data = await state.get_data()

    if data['is_hard'] is True:
        await message.answer(text=l10n.format_value('send-homework'))
        await insert_homework(user_id=message.from_user.id, task_id=data['id_task'],
                              is_hard=True, answer=data['answer'])
        await state.clear()
    else:
        if data['answer'] == data['solved']:
            await message.answer(text=l10n.format_value('correct'))
            await insert_homework(user_id=message.from_user.id, task_id=data['id_task'],
                                  is_hard=False, answer=data['answer'])
            await state.clear()
        else:
            await message.answer(text=l10n.format_value('incorrect'))


@student_router.message(Command("student"))
async def check_handler(message: Message, l10n: FluentLocalization):
    await message.answer(text='Привет, Студент!')