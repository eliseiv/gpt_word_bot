import os
import shutil


def sort_html_files(source_folder):
    yes_folder = os.path.join(source_folder, 'YES')
    now_folder = os.path.join(source_folder, 'NOT')

    os.makedirs(yes_folder, exist_ok=True)
    os.makedirs(now_folder, exist_ok=True)

    for filename in os.listdir(source_folder):
        if filename.endswith('.html'):
            file_path = os.path.join(source_folder, filename)

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            if 'Tone' in content:
                shutil.copy(file_path, os.path.join(yes_folder, filename))
            else:
                shutil.copy(file_path, os.path.join(now_folder, filename))


# Пример использования
# Укажите путь к папке с HTML-файлами
source_directory = r'C:\\Users\\DellXPS\\Downloads\\Python\\gpt_word_bot\\docs'
sort_html_files(source_directory)
