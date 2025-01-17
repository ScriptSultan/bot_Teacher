# Bot for teacher and student
## Предисловие:
Бот был сделан для помощи ученикам в подготовке к ЕГЭ и учителям для упрощения ведения их успеваемости.
## Установка

### Системные требования:
1. Python 3.9 и выше;
2. Linux (должно работать на Windows, но могут быть сложности с установкой);
3. Systemd (для запуска через systemd);
### Протестировать на своем локальном сервере:
1. Клонируйте репозиторий;
2. Перейдите (`cd`) в клонированный каталог и создайте виртуальное окружение Python (Virtual environment, venv);
3. Активируйте venv и установите все зависимости из `requirements.txt`;
4. Скопируйте `env_example` под именем `.env`, откройте его и заполните переменные;
5. Внутри активированного venv: `python -m main`.
### Загрузка на сервер
1. Выполните шаги 1-4 из раздела "Протестировать на своем локальном сервере" выше;
2. Скопируйте `bot_ege_check.example.service` в `bot_ege_check.service`, откройте и отредактируйте переменные `WorkingDirectory`,
 `ExecStart` и `Description`;
3. Cкопируйте (или создайте симлинк) файла службы в каталог `/etc/systemd/system/`;
4. Активируйте сервис и запустите его: `sudo systemctl enable bot_ege_check`;
5. Проверьте, что сервис запустился: `systemctcl status bot_ege_check` (можно без root-прав).
