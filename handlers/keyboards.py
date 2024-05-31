from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluent.runtime import FluentLocalization

from models.list_task import subject, task_list


# Клавиатуры юзера
def setting_role(affiliate, l10n: FluentLocalization):
    menu = InlineKeyboardBuilder()
    menu.button(text=l10n.format_value('i-am-student'), callback_data=f'student_{affiliate}')
    menu.button(text=l10n.format_value('i-am-teacher'), callback_data='teacher')
    menu.adjust(1, 1)
    return menu.as_markup()
#

# Клавиатуры админа
def kb_confirm(user_id, fullname, username, l10n: FluentLocalization):
    confirm = InlineKeyboardBuilder()
    confirm.button(text=l10n.format_value('confirm-teacher'),
                   callback_data=f'confirm:{user_id}:{username}:{fullname}')
    confirm.button(text=l10n.format_value('cancel-teacher'), callback_data='delete')
    confirm.adjust(2)
    return confirm.as_markup()


def kb_subject_admin():
    subjects = InlineKeyboardBuilder()
    for subj in subject.keys():
        subjects.button(text=subj, callback_data=f'admin_subj:{subj}')
    subjects.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1)
    return subjects.as_markup()


# Клавиатуры преподавателя
def kb_main_teacher(l10n: FluentLocalization):
    menu = InlineKeyboardBuilder()
    menu.button(text=l10n.format_value('students'), callback_data='list_student')
    menu.button(text=l10n.format_value('add-task'), callback_data='add_exercise')
    menu.adjust(1, 1)
    return menu.as_markup()


def kb_subject_teacher():
    subjects = InlineKeyboardBuilder()
    for subj in subject.keys():
        subjects.button(text=subj, callback_data=f'subj:{subj}')
    subjects.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1)
    return subjects.as_markup()


def kb_list_students(list_student):
    list_s = InlineKeyboardBuilder()
    for student in list_student:
        list_s.button(text=student[0], callback_data=f'person:{student[0]}:{student[1]}')
    list_s.adjust()
    return list_s.as_markup()


def kb_person(user_teleg_fullname, user_id, l10n: FluentLocalization):
    menu = InlineKeyboardBuilder()
    menu.button(text=l10n.format_value('statistics'), callback_data=f'statistic:{user_teleg_fullname}:{user_id}')
    menu.button(text=l10n.format_value('check-homework'), callback_data=f'homework:{user_id}')
    # menu.button(text='', callback_data='')
    menu.adjust(1, 1)
    return menu.as_markup()


def kb_next_static(user_id, l10n: FluentLocalization):
    menu = InlineKeyboardBuilder()
    menu.button(text=l10n.format_value('back-to-student'), callback_data='list_student')
    menu.button(text=l10n.format_value('check-homework'), callback_data=f'homework:{user_id}')
    # menu.button(text='', callback_data='')
    menu.adjust(1, 1)
    return menu.as_markup()


def kb_get_hardtask(hardtask_id, user_id, l10n: FluentLocalization):
    menu = InlineKeyboardBuilder()
    menu.button(text=l10n.format_value('show-task'), callback_data=f'get_hardtask:{hardtask_id}:{user_id}')
    menu.button(text=l10n.format_value('confirm-teacher'), callback_data=f'complete:{hardtask_id}:{user_id}')
    menu.button(text=l10n.format_value('cancel-teacher-'), callback_data=f'cancel:{hardtask_id}:{user_id}')
    # menu.button(text='', callback_data='')
    menu.adjust(1, 2)
    return menu.as_markup()


# Клавиатуры ученика
def kb_main_student(l10n: FluentLocalization, ref_id, subj=None):
    menu = InlineKeyboardBuilder()
    menu.button(text=l10n.format_value('first-tasks'), callback_data='first_tasks')
    menu.button(text=l10n.format_value('hard-task'), callback_data='hard_task')
    menu.button(text=l10n.format_value('kim'), callback_data='kim')
    if ref_id is not None:
        menu.button(text=l10n.format_value('homework'), callback_data='work_teacher')
    if subj is None:
        menu.button(text=l10n.format_value('set-subject'), callback_data='set_course')
    else:
        menu.button(text=f"[{subj}]", callback_data='set_course')
    menu.adjust(2, 1, 1)
    return menu.as_markup()


def kb_tasks(subj, callback_data, l10n: FluentLocalization):
    tasks = InlineKeyboardBuilder()
    if subj is None:
        return None
    else:
        if callback_data == 'first_tasks':
            for i in range(1, subject[subj][0]):
                tasks.button(text=f'{i}. {task_list[subj][i]}', callback_data=f'task:first:{subj}:{i}')
        elif callback_data == 'hard_task':
            for i in range(subject[subj][0], subject[subj][1]+1):
                tasks.button(text=f'{i}. {task_list[subj][i]}', callback_data=f'task:hard:{subj}:{i}')
        tasks.button(text=l10n.format_value('random-task'), callback_data=f'random:{subj}:{callback_data}')
        tasks.button(text=l10n.format_value('back'), callback_data='back_main')
        tasks.adjust(1, 1, 1, 1, 1)
        return tasks.as_markup()


def kb_subj_student():
    subjects = InlineKeyboardBuilder()
    for subj in subject.keys():
        subjects.button(text=subj, callback_data=f'stud_subj:{subj}')
    subjects.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1)
    return subjects.as_markup()


def kb_list_tasks(list_task, subj, l10n: FluentLocalization):
    tasks = InlineKeyboardBuilder()
    for i in range(len(list_task)):
        if list_task[i]:

            for task in list_task[i]:
                if task[0] < subject[subj][0]:
                    tasks.button(text=f'{task[0]}. {task_list[subj][task[0]]}', callback_data=f'taperson:task:{task[4]}')
                else:
                    tasks.button(text=f'{task[0]}. {task_list[subj][task[0]]}', callback_data=f'taperson:hardtask:{task[3]}')
    tasks.button(text=l10n.format_value('back'), callback_data='back_main')
    tasks.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return tasks.as_markup()


def kb_set_answer(task_id: int, is_hard: bool, l10n: FluentLocalization):
    answer = InlineKeyboardBuilder()
    task = 'task' if is_hard is False else 'hardtask'
    answer.button(text=l10n.format_value('set-answer'), callback_data=f'check-answer:{task}:{task_id}')
    answer.adjust(1)
    return answer.as_markup()


def kb_task_again(subj, is_hard: bool, l10n: FluentLocalization):
    again = InlineKeyboardBuilder()
    task = 'task' if is_hard is False else 'hardtask'
    again.button(text=l10n.format_value('back'), callback_data=f'task_again:{subj}')
    again.button(text=l10n.format_value('back'), callback_data='back_main')
    again.adjust(1, 1)
    return again.as_markup()