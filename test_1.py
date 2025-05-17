import json
import os
import time
import logging
from seleniumbase import SB
from typing import Optional
from links import links_1
from proxys import proxys_1
from selenium.webdriver.common.keys import Keys
import pyperclip

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(SCRIPT_DIR, "docs")
PROMPT_FILE = os.path.join(SCRIPT_DIR, "promt.txt")

login = 'copabix905@sportizi.com'
password = 'fuFj7CIB'

# Создаем папку, если она не существует
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def get_pending_links(links, save_dir):
    """Возвращает список ссылок, для которых еще нет сохраненных файлов."""
    pending = []
    for link in links:
        safe_filename = "".join(
            c for c in link if c.isalnum() or c in ('-', '_'))
        output_file = os.path.join(save_dir, f"{safe_filename}.html")
        if not os.path.exists(output_file):
            pending.append(link)
    return pending


class SBDriver:
    @staticmethod
    def fetch_content(url: str):
        """Обрабатывает список ссылок, меняя прокси для каждой ссылки."""
        pending_links = get_pending_links(links_1, SAVE_DIR)
        proxy_index = 0
        total_proxies = len(proxys_1)

        while pending_links:
            for current_link in list(pending_links):
                # Выбираем и обновляем прокси для каждой ссылки
                proxy_domen = proxys_1[proxy_index]
                proxy_index = (proxy_index + 1) % total_proxies

                try:
                    with SB(uc=True, browser='chrome', proxy=f'socks5://{proxy_domen}') as sb:
                        sb.open(url)
                        sb.wait_for_ready_state_complete()
                        sb.sleep(10)
                        
                        try:
                            sign_in_btn = '//*[@id="conversation-header-actions"]/div/button[1]'
                            sb.click(sign_in_btn)

                        except Exception as e:
                            print(e)

                        mail = '//*[@id=":r1:-email"]'
                        sb.click(mail)

                        sb.driver.switch_to.active_element.send_keys(login)
                        next_login = '//*[@id=":r1:"]/div[2]/button'
                        sb.click(next_login)

                        password_area = '//*[@id=":re:-password"]'
                        sb.click(password_area)
                        sb.driver.switch_to.active_element.send_keys(password)

                        next_password = '//*[@id=":re:"]/div[2]/button'
                        sb.click(next_password)
                        sb.sleep(15)

                        web_search = '//*[@id="thread-bottom"]/div/div/div[2]/form/div[1]/div/div[2]/div/div[1]/div[2]/div/span/div/button'
                        
                        if sb.is_element_present(web_search):
                            sb.click(web_search)
                        else:
                            print('Кнопки поиска не найдено')


                        # Ввод prompt
                        input_area_xpath = '//*[@id="prompt-textarea"]/p'
                        button_send = '//*[@id="composer-submit-button"]'
                        sb.click(input_area_xpath)
                        sb.sleep(2)
                        try:
                            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                                prompt_content = f.read()
                            pyperclip.copy(current_link + prompt_content)
                            logging.info(
                                f"Содержимое {PROMPT_FILE} скопировано в буфер обмена, длина: {len(prompt_content)} символов")
                        except FileNotFoundError:
                            logging.error(f"Файл {PROMPT_FILE} не найден!")
                            continue

                        sb.driver.switch_to.active_element.send_keys(
                            Keys.CONTROL + "v")
                        sb.sleep(5)
                        sb.click(button_send)
                        sb.sleep(90)

                        # Извлечение outer_html
                        full_xpath = (
                            "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div[2]/div/div/div[2]/article[2]/div"
                        )
                        outer_html = sb.execute_script(f"""
                            const element = document.evaluate(
                                '{full_xpath}',  
                                document,  
                                null,  
                                XPathResult.FIRST_ORDERED_NODE_TYPE,  
                                null
                            ).singleNodeValue;
                            return element ? element.outerHTML : null;
                        """)

                        # Сохранение результата
                        safe_filename = "".join(
                            c for c in current_link if c.isalnum() or c in ('-', '_'))
                        output_file = os.path.join(
                            SAVE_DIR, f"{safe_filename}.html")
                        with open(output_file, "w", encoding="utf-8") as file:
                            file.write(outer_html or "")
                        logging.info(f"Сохранен файл: {output_file}")
                        pending_links.remove(current_link)

                except Exception as err:
                    logging.error(
                        f"Ошибка при обработке {current_link}: {err}")

                time.sleep(100)

            if pending_links:
                logging.info(
                    f"Осталось {len(pending_links)} необработанных ссылок. Повторная попытка...")
                time.sleep(100)


if __name__ == "__main__":
    try:
        url = 'https://chatgpt.com/'
        SBDriver.fetch_content(url)
    except KeyboardInterrupt:
        logging.info("Процесс прерван пользователем.")
