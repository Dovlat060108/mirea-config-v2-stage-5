# Практическая работа №1. Этап 4: Основные команды

**Дисциплина:** Конфигурационное управление  
**Студент:** Алиев Довлат Фазильевич  
**Группа:** ИКБО-62-25  
**Вариант:** 2  
**Репозиторий:** https://github.com/Dovlat060108/mirea-config-v2-stage-4  
**Ветка этапа:** `stage-4`

## Общее описание

Консольный эмулятор UNIX-подобной оболочки на Python 3.10+.
Эта версия включает этапы 1-4. Внешние библиотеки не нужны.
Приглашение использует имя пользователя и имя компьютера реальной ОС.
Парсер разделяет ввод по пробельным символам. Кавычки, конвейеры,
перенаправления и раскрытие переменных окружения не поддерживаются.
Команды эмулятора не запускают программы реальной ОС.

## Реализованные этапы

1. REPL, парсер, приглашение ОС, заглушки ls/cd, exit и ошибки.
2. Параметры запуска, отладочный вывод, скрипты и комментарии #.
3. Загрузка JSON VFS и base64 в память, проверка формата и путей.
4. Рабочие ls, cd, tac, date и find.

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


## Формат виртуальной файловой системы

```json
{
  "nodes": [
    {"path": "/docs", "type": "dir"},
    {"path": "/docs/a.txt", "type": "file", "content": "one\ntwo\n"},
    {"path": "/binary.bin", "type": "file",
     "encoding": "base64", "content": "AP8="}
  ]
}
```

Корневой каталог / создаётся автоматически и не записывается в nodes.
Все пути абсолютные и уникальные; родитель файла должен быть каталогом.
Порядок узлов произвольный. encoding: utf-8 (по умолчанию) или base64.
Пустое содержимое файла допустимо. Поле content хранит строку.
Загрузка полностью выполняется в памяти, исходный JSON не изменяется.
При перезапуске все изменения VFS исчезают. Символические ссылки и
права доступа не моделируются. Нет распаковки и записи в реальную ФС.

```sh
sh scripts/demo-vfs.sh
```

Скрипт проверяет минимальную VFS, несколько файлов и вложенность
не менее трёх уровней. Файлы: minimal.json, files.json, vfs.json.

## Команды и примеры

- `exit`: завершить сеанс; аргументы запрещены.
- `ls [путь]`: отсортированные прямые дети каталога или имя файла.
- `cd [каталог]`: переход в каталог; без аргумента переход в /.
- `tac файл [файл ...]`: строки каждого UTF-8 файла в обратном порядке.
- `date [+формат]`: местные дата/время ОС; формат Python strftime.
- `find [путь] [-name шаблон]`: рекурсивный поиск, включая исходный узел;
  -name фильтрует имя по шаблону *, ? и []. По умолчанию путь равен .

Поддержаны абсолютные и относительные пути, . и ..; переход выше /
оставляет пользователя в корне. tac выводит строки с обычным переводом
строки; побайтовое поведение GNU tac для файлов без конечного переноса
не воспроизводится. Другие параметры UNIX-команд не поддерживаются.

```text
ls /docs
a
notes.txt
tac /docs/notes.txt
third
second
first
find /docs -name *.txt
/docs/a/b/c.txt
/docs/notes.txt
```

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

При подготовке выполнено 20 автоматических тестов; все прошли.
Тесты проверяют результаты команд, неверные аргументы и обработку ошибок.

## Функции исходного кода

- `commands.require_count`: Validate argument count and reject unsupported options.
- `Commands.__init__`: Keep references to shell state and the loaded VFS.
- `Commands.ls`: List directory children or the supplied file name.
- `Commands.cd`: Change directory; no arguments return to the VFS root.
- `Commands.tac`: Concatenate files with their line order reversed per file.
- `Commands.date`: Show local OS date/time or one strftime format with + prefix.
- `Commands.find`: Recursively list paths, optionally filtering by -name glob.
- `commands.install`: Register the five fully implemented stage-four commands.
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
- `vfs.normalize`: Resolve relative paths and dot components from the VFS root.
- `VFS.__init__`: Create an empty root directory.
- `VFS.load`: Read and validate JSON without extracting or writing files.
- `VFS.add`: Validate one unique node and decode optional base64 content.
- `VFS.decode`: Decode UTF-8 text or strict base64, rejecting other formats.
- `VFS.node`: Return a node or a readable missing-path error.
- `VFS.directory`: Require an existing directory.
- `VFS.children`: List sorted direct children only.
- `VFS.text`: Read a UTF-8 file; binary and directory input are errors.

## Структура

- src/: исходный код, main.py - точка входа.
- tests/: автоматические тесты unittest.
- examples/: демонстрационные команды и данные.
- scripts/: сценарии реальной ОС для демонстрации.
- run.sh, run.bat, Makefile: запуск и тестирование.
- .gitignore: исключение временных файлов и результатов сборки.

PDF README предназначен для загрузки в СДО вместе с URL репозитория.
PDF и архивы не добавляются в исходный git-репозиторий.
