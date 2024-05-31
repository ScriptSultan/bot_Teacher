import random
from typing import Any

from sqlalchemy import Integer, Column, String, BigInteger, ForeignKey, select, insert, or_, update, bindparam, \
    delete, func, text, Row
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models.config import settings
from models.list_task import subject
from models.models import User, Teachers, Tasks, HardTasks, Homeworks

async_engine = create_async_engine(settings.db_url, echo=settings.echo)

async_session = async_sessionmaker(async_engine, expire_on_commit=True)


# async def lala():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


async def create_profile(user_id: int, username: str, fullname: str, is_teacher: bool, subj: str = None, link=None,
                         teacher_name=None, ref=None, student_name: str = None) -> None:
    async with async_session() as session:
        user_teacher = (await session.execute(select(Teachers.id).filter_by(teacher_id=user_id).union(
            select(User.id).filter_by(user_id=user_id)))).all()

        if is_teacher is True and not user_teacher:
            # Генерация реферального кода
            ref_id = username[0:3] + str(user_id)[0:5]

            user = Teachers(teacher_id=user_id, teacher_username=username, teacher_teleg_fullname=fullname,
                            teacher_ref=ref_id, teacher_link=link, teacher_name=teacher_name, subject=subj)
            session.add(user)

        elif is_teacher is False and not user_teacher:
            user = User(user_id=user_id, user_name=username, user_teleg_fullname=fullname,
                        teacher_ref=ref, student_name=student_name)
            session.add(user)

        else:
            await update_profile(user_id=user_id, username=username, user_tg_fullname=fullname, is_teacher=is_teacher)

        await session.commit()


async def update_profile(user_id: int, username: str, user_tg_fullname: str, is_teacher: bool) -> None:
    async with async_session() as session:

        if is_teacher is True:
            await session.execute(update(Teachers).where(
                Teachers.teacher_id == user_id).values(teacher_username=username,
                                                       teacher_teleg_fullname=user_tg_fullname))
        else:
            await session.execute(update(User).where(
                User.user_id == user_id).values(user_name=username, user_teleg_fullname=user_tg_fullname))
        await session.commit()


async def get_ref_subj(user_id: int) -> Row[tuple[Any, Any]] | None:
    async with async_session() as session:
        resp = await session.execute(select(Teachers.teacher_ref, Teachers.subject).filter_by(teacher_id=user_id))
        return resp.first()


async def insert_task(user_id: int, number_task: int, txt: str = None, file_id: str = None, answer: int = None, subj=None) -> None:
    if subj is None:
        ref_subj = await get_ref_subj(user_id)
        subj_t = ref_subj[1]
        ref = ref_subj[0]
    else:
        ref = None
        subj_t = subj

    async with async_session() as session:
        if number_task >= subject[subj_t][0]:
            task = HardTasks(tasks_photo=file_id, tasks_text=txt,
                             teacher_ref=ref, number_hard_task=number_task,
                             subject=subj_t)

        else:
            task = Tasks(tasks_photo=file_id, tasks_text=txt, solved=answer,
                         teacher_ref=ref, number_task=number_task, subject=subj_t)

        session.add(task)
        await session.commit()


async def get_subj_from_teacher(user_id):
    async with async_session() as session:
        result = await session.execute(select(Teachers.subject).join(User).where(
            Teachers.teacher_ref == (select(User.teacher_ref).where(User.user_id == user_id)).as_scalar()))
        return result.scalar()


async def get_subj_ref_from_student(user_id):
    async with async_session() as session:
        ref = await session.execute(select(User.subjects, User.teacher_ref).filter_by(user_id=user_id))
        return ref.first()
#


async def update_subj_student(user_id, subj):
    async with async_session() as session:
        await session.execute(update(User).where(User.user_id == user_id).values(subjects=subj))
        await session.commit()


async def get_task(number_task, is_hard: bool, subj):
    async with async_session() as session:
        if is_hard is False:
            resp = await session.execute(select(
                Tasks.tasks_photo, Tasks.tasks_text, Tasks.solved).filter_by(teacher_ref=None, number_task=number_task, subject=subj))
        else:
            resp = await session.execute(select(
                HardTasks.tasks_photo, HardTasks.tasks_text).filter_by(teacher_ref=None, number_hard_task=number_task, subject=subj))
        task = random.choice(resp.all())
        return task


async def get_list_teacher():
    async with async_session() as session:
        resp = await session.execute(select(Teachers.teacher_id))
        return resp.scalars().all()


async def get_list_student():
    async with async_session() as session:
        resp = await session.execute(select(User.user_id))
        return resp.scalars().all()


async def get_list_student_for_teacher(user_id):
    async with async_session() as session:
        result = await session.execute(select(User.student_name, User.user_id).join(Teachers).where(
            Teachers.teacher_ref == (select(Teachers.teacher_ref).where(Teachers.teacher_id == user_id)).as_scalar()))
        return result.all()


async def get_statistic_person(user_id):
    async with async_session() as session:
        statistic_completed = await session.execute(
            select(Homeworks.id).filter_by(id_user=user_id, solved_homework=True))
        statistic_completed = len(statistic_completed.all())

        statistic_not_check = await session.execute(
            select(Homeworks.id).filter_by(id_user=user_id, solved_homework=False))
        statistic_not_check = len(statistic_not_check.all())

        statistic_false = await get_list_homework(user_id=user_id)
        statistic_false = len(statistic_false[0]) + len(statistic_false[1])

        return statistic_completed, statistic_not_check, statistic_false


async def get_homework_false(user_id):
    async with async_session() as session:
        homework_not_check = await session.execute(
            select(Homeworks.id_hardtask, Homeworks.answer_user).filter_by(id_user=user_id, solved_homework=False))
        return homework_not_check.all()


async def get_hardtask(hardtask_id):
    async with async_session() as session:
        hardtask = await session.execute(
            select(HardTasks.tasks_photo, HardTasks.tasks_text).filter_by(id=hardtask_id))
        return hardtask.first()


async def get_list_homework(user_id):
    async with async_session() as session:
        smth = select(Tasks.number_task, Tasks.tasks_photo, Tasks.tasks_text, Tasks.solved, Tasks.id).outerjoin(
            Homeworks, (Tasks.id == Homeworks.id_task) & (Homeworks.id_user == user_id)).filter_by(id_task=None)

        smth_2 = select(HardTasks.number_hard_task, HardTasks.tasks_photo, HardTasks.tasks_text,
                        HardTasks.id).outerjoin(Homeworks, (HardTasks.id == Homeworks.id_hardtask) & (
            Homeworks.id_user == user_id)).filter_by(id_hardtask=None)

        task = await session.execute(smth)
        hard_task = await session.execute(smth_2)
        return task.all(), hard_task.all()


async def get_task_by_id(user_id, is_hard: bool, task_id):
    ref = await get_subj_ref_from_student(user_id)
    async with async_session() as session:

        if is_hard is False:
            tasks = await session.execute(select(
                Tasks.id, Tasks.tasks_photo, Tasks.tasks_text, Tasks.solved, Tasks.teacher_ref).filter_by(
                teacher_ref=ref[1], id=task_id))
        else:
            tasks = await session.execute(select(
                HardTasks.id, HardTasks.tasks_photo, HardTasks.tasks_text, HardTasks.teacher_ref).filter_by(
                teacher_ref=ref[1], id=task_id))
        return tasks.first()


async def insert_homework(user_id, is_hard: bool, task_id, answer):
    async with async_session() as session:
        if is_hard is True:
            homework = Homeworks(id_user=user_id, id_hardtask=task_id, answer_user=answer, solved_homework=False)
        else:
            homework = Homeworks(id_user=user_id, id_task=task_id, answer_user=answer, solved_homework=True)
        session.add(homework)
        await session.commit()


async def cancel_homework(user_id, hardtask_id):
    async with async_session() as session:
        cancel_homework = await session.execute(delete(Homeworks).filter_by(id_user=user_id, id_hardtask=hardtask_id))
        await session.commit()


async def complete_homework(user_id, hardtask_id):
    async with async_session() as session:
        await session.execute(
            update(Homeworks).where(Homeworks.id_user == user_id,
                                    Homeworks.id_hardtask == hardtask_id).values(solved_homework=True))
        await session.commit()