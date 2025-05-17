import os
from pathlib import Path

# Импорт массива ссылок из файла links.py
from all_links import links_1

# Удаление дубликатов, сохраняя порядок
links_1 = list(dict.fromkeys(links_1))

# Папка с файлами
DOCS_FOLDER = "docs"

# Получаем список файлов без расширений
existing_files = {
    file.stem.replace(".html", "").replace(".", "")
    for file in Path(DOCS_FOLDER).glob("*.html")
}

# Разделяем ссылки на два списка
active_links = []
used_links = []

for link in links_1:
    # Приводим к такому же формату, как в списке файлов
    clean_link = link.replace(".", "")
    if clean_link in existing_files:
        used_links.append(f'# "{link}"')  # Комментируем строку
    else:
        active_links.append(f'"{link}"')

# Записываем результат в новый файл
with open("updated_links.py", "w", encoding="utf-8") as f:
    f.write("links_1 = [\n")
    for link in active_links:
        f.write(f"    {link},\n")
    f.write("]\n\n")  # Разделяем списки

    f.write("used = [\n")
    for link in used_links:
        f.write(f"    {link},\n")
    f.write("]\n")

print("Файл updated_links.py создан.")
