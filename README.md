# Task 1

## Задание

1. **Скачивание страниц**:
   - Из предварительно подготовленного списка сайтов краулером было выкачано минимум 100 текстовых страниц.
   - Страницы содержат текст и HTML-разметку (очистка HTML не требуется).
   - Язык текста на всех страницах одинаков.

2. **Запись страниц**:
   - Каждая выкачанная страница сохранена в отдельный текстовый файл (содержит HTML-разметку).
   
3. **Индексный файл**:
   - Для удобства была создана таблица в файле `index.txt`, в которой хранится номер файла и соответствующая ссылка на страницу.

## Структура проекта

- `scraper.py` - Скрипт краулера для скачивания страниц.
- `index.txt` - Индексный файл с номерами файлов и ссылками на страницы.
- `выкачка.txt` - Файл содержащий текст с каждой страницы (включая HTML разметку)
- `pages.zip` - Архив, в котором находятся выкачанные страницы в формате `.html`.

## Как использовать

1. Клонируйте репозиторий:
   ```
   git clone <URL>
   ```
   
2. Перейдите в папку проекта
   ```
   cd <project-directory>
   ```
   
3. Запустите скрипт
   ```
   python scraper.py
   ```