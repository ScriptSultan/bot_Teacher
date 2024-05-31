import datetime

from sqlalchemy import create_engine, Integer, String, BigInteger, ForeignKey, func, Column
from sqlalchemy.orm import Session, as_declarative, declared_attr, Mapped, mapped_column, sessionmaker, relationship, \
    DeclarativeBase


# class Base(DeclarativeBase):
#     pass
@as_declarative()
class AbstractModel:
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    # Называет таблицы как классы
    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class User(AbstractModel):
    # __tablename__ = 'user'
    # id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    user_name: Mapped[str] = mapped_column(unique=True)  # заполняет сам пользователь при регистрации
    user_teleg_fullname: Mapped[str] = mapped_column()
    student_name: Mapped[str] = mapped_column()
    subjects: Mapped[str] = mapped_column(nullable=True)
    teacher_ref: Mapped[str] = mapped_column(ForeignKey('teachers.teacher_ref'), nullable=True)
    create_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    teacher: Mapped['Teachers'] = relationship(back_populates="users")

    user: Mapped[list['Homeworks']] = relationship(back_populates="homework", uselist=True)


class Tasks(AbstractModel):  # таблица заданий из 1 части
    # __tablename__ = 'tasks'
    # id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    tasks_photo: Mapped[str] = mapped_column(server_default=None, nullable=True)  # задание в формате фото
    tasks_text: Mapped[str] = mapped_column(server_default=None, nullable=True)  # задание в формате текста
    number_task: Mapped[int] = mapped_column()
    subject: Mapped[str] = mapped_column()
    solved: Mapped[int] = mapped_column()  # правильный ответ

    teacher_ref: Mapped[str] = mapped_column(ForeignKey('teachers.teacher_ref'), nullable=True)
    teacher: Mapped['Teachers'] = relationship(back_populates="tasks", uselist=False)

    homework: Mapped[list['Homeworks']] = relationship(back_populates="homework_task", uselist=True)


class HardTasks(AbstractModel):  # таблица заданий из 2 части
    # __tablename__ = 'hardtasks'
    # id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    tasks_photo: Mapped[str] = mapped_column(server_default=None, nullable=True)  # задание в формате фото
    tasks_text: Mapped[str] = mapped_column(server_default=None, nullable=True)  # задание в формате текста
    number_hard_task: Mapped[int] = mapped_column()
    subject: Mapped[str] = mapped_column()

    teacher_ref: Mapped[str] = mapped_column(ForeignKey('teachers.teacher_ref'), nullable=True)
    teacher: Mapped['Teachers'] = relationship(back_populates="hard_tasks", uselist=False)

    homework: Mapped[list['Homeworks']] = relationship(back_populates="homework_hardtask", uselist=True)


class Teachers(AbstractModel):
    # __tablename__ = 'teachers'
    # id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    teacher_name: Mapped[str] = mapped_column(nullable=True)  # заполняет сам преподавателем при регистрации
    teacher_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    teacher_username: Mapped[str] = mapped_column(unique=True)
    teacher_link: Mapped[str] = mapped_column(nullable=True)  # заполняет сам препод при регистрации (ссылка на профиль в интернете)
    teacher_teleg_fullname: Mapped[str] = mapped_column()
    teacher_ref: Mapped[str] = mapped_column(unique=True, nullable=True)
    subject: Mapped[str] = mapped_column()

    tasks: Mapped[list['Tasks']] = relationship(back_populates="teacher", uselist=True)
    hard_tasks: Mapped[list['HardTasks']] = relationship(back_populates="teacher", uselist=True)

    users: Mapped[list['User']] = relationship(back_populates="teacher", uselist=True)
    create_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class Homeworks(AbstractModel):
    # __tablename__ = 'homeworks'
    # id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    id_user: Mapped[int] = mapped_column(ForeignKey('user.user_id'), nullable=True) # главная у юзеров
    homework: Mapped['User'] = relationship(back_populates="user", uselist=False)

    id_task: Mapped[int] = mapped_column(ForeignKey('tasks.id'), nullable=True) # главная у таксов
    homework_task: Mapped['Tasks'] = relationship(back_populates="homework", uselist=False)

    id_hardtask: Mapped[int] = mapped_column(ForeignKey('hardtasks.id'), nullable=True) # главная у hard_таксов
    homework_hardtask: Mapped['HardTasks'] = relationship(back_populates="homework", uselist=False)

    answer_user: Mapped[str] = mapped_column(nullable=True)
    solved_homework: Mapped[bool] = mapped_column(nullable=True)

    create_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
