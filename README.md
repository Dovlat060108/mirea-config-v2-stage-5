# Практическая работа №1. Этап 2: Конфигурация

**Дисциплина:** Конфигурационное управление  
**Студент:** Алиев Довлат Фазильевич  
**Группа:** ИКБО-62-25  
**Вариант:** 2  
**Репозиторий:** https://github.com/Dovlat060108/mirea-config-v2-stage-2  
**Ветка этапа:** `stage-2`

## Общее описание

Консольный эмулятор UNIX-подобной оболочки на Python 3.10+.
Эта версия включает этапы 1-2. Внешние библиотеки не нужны.
Приглашение использует имя пользователя и имя компьютера реальной ОС.
Парсер разделяет ввод по пробельным символам. Кавычки, конвейеры,
перенаправления и раскрытие переменных окружения не поддерживаются.
Команды эмулятора не запускают программы реальной ОС.

## Реализованные этапы

1. REPL, парсер, приглашение ОС, заглушки ls/cd, exit и ошибки.
2. Параметры запуска, отладочный вывод, скрипты и комментарии #.

## Сборка, запуск и тестирование

Отдельная сборка не требуется: Python исполняет исходный код.
Все команды запускаются из корня репозитория.

```sh
python3 --version
sh run.sh
make test
# Равнозначный запуск тестов без make:
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Windows: `run.bat`; тесты: `set PYTHONPATH=src`, затем
`python -m unittest discover -s tests -v`.


```sh
sh run.sh --vfs examples/vfs.json --script examples/startup.txt --no-repl
sh scripts/demo-config.sh
sh scripts/demo-errors.sh
```

## Настройки и стартовый скрипт

- `--vfs ПУТЬ`: JSON-файл VFS; по умолчанию `examples/vfs.json`.
- `--script ПУТЬ`: UTF-8 файл команд; по умолчанию не задан.
- `--no-repl`: завершение после стартового скрипта без интерактивного ввода.
- `--help`: справка по параметрам командной строки.

При запуске выводятся все заданные параметры. В скрипте поддержаны
отдельные и встроенные комментарии Python: текст после # игнорируется.
Ввод каждой команды выводится вместе с приглашением, затем выводится ответ.
При ошибке показываются сообщение, имя скрипта и номер строки.
Выполнение продолжается; итоговый код возврата равен 1 при любой ошибке.
Команда exit останавливает скрипт и REPL. Успешный запуск возвращает 0.

На этом этапе путь VFS только хранится и выводится; загрузка реализована на этапе 3.

## Команды и примеры

- `exit`: завершить сеанс; аргументы запрещены.
- `ls [путь]`, `cd [путь]`: заглушки; печатают имя и список аргументов.

## Демонстрация ошибок

```text
unknown
Ошибка: неизвестная команда: unknown
exit extra
Ошибка: использование: exit
```

`examples/errors.txt` содержит намеренные ошибки. Скрипт
`demo-errors.sh` проверяет ожидаемый ненулевой код возврата.

## Проверка

При подготовке выполнено 9 автоматических тестов; все прошли.
Тесты проверяют результаты команд, неверные аргументы и обработку ошибок.

## Функции исходного кода

- `config.arguments`: Parse VFS/script locations and an optional noninteractive mode.
- `config.run_script`: Echo script commands, skip Python comments, report each error.
- `main.main`: Initialize and run the current stage.
- `shell.parse`: Split a command by whitespace, without quotes or expansion.
- `Shell.__init__`: Register the commands provided by the current stage.
- `Shell.prompt`: Use the actual OS username and hostname in the prompt.
- `Shell.execute`: Return success; display errors and keep the session usable.
- `Shell.stub`: Validate prototype ls/cd arguments and show their values.
- `Shell.exit`: Stop the current shell; exit accepts no arguments.
- `Shell.repl`: Read commands until exit, EOF or keyboard interrupt.

## Структура

- src/: исходный код, main.py - точка входа.
- tests/: автоматические тесты unittest.
- examples/: демонстрационные команды и данные.
- scripts/: сценарии реальной ОС для демонстрации.
- run.sh, run.bat, Makefile: запуск и тестирование.
- .gitignore: исключение временных файлов и результатов сборки.

PDF README предназначен для загрузки в СДО вместе с URL репозитория.
PDF и архивы не добавляются в исходный git-репозиторий.
