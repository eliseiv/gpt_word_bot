import os
import pypandoc

# Автоматически загружаем pandoc, если он не установлен
try:
    pypandoc.get_pandoc_version()  # Проверяем, установлен ли pandoc
except OSError:
    print("Pandoc не найден. Загружаем автоматически...")
    pypandoc.download_pandoc()  # Загружает pandoc в домашнюю директорию пользователя


def ensure_html_structure(html_content):
    """Проверяет и оборачивает HTML в теги <html><body>, если их нет."""
    html_content = html_content.strip()
    if not html_content.startswith('<html'):
        html_content = '<html>\n<body>\n' + html_content
    if not html_content.endswith('</html>'):
        html_content += '\n</body>\n</html>'
    return html_content


def convert_html_to_docx(input_folder, output_folder):
    """Конвертирует все HTML-файлы из input_folder в .docx в output_folder."""
    # Создаем папку для вывода, если ее нет
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Обрабатываем каждый HTML-файл в папке
    for filename in os.listdir(input_folder):
        if filename.endswith('.html'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(
                output_folder, filename.replace('.html', '.docx'))

            # Читаем HTML-файл
            with open(input_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Оборачиваем в теги, если нужно
            html_content = ensure_html_structure(html_content)

            # Сохраняем временный HTML-файл с правильной структурой
            temp_html_path = os.path.join(input_folder, 'temp.html')
            with open(temp_html_path, 'w', encoding='utf-8') as temp_file:
                temp_file.write(html_content)

            # Конвертируем в .docx с помощью pandoc
            pypandoc.convert_file(temp_html_path, 'docx',
                                  outputfile=output_path)

            # Удаляем временный файл
            os.remove(temp_html_path)

            print(f"Конвертирован: {filename} -> {output_path}")


if __name__ == "__main__":
    # Укажите папки для входных и выходных файлов
    # Папка с HTML-файлами
    input_folder = "D:\\Python\\gpt_word_bot\\docs"
    # Папка для сохранения .docx
    output_folder = "D:\\Python\\gpt_word_bot\\output_folder"

    convert_html_to_docx(input_folder, output_folder)
