import json
import os
import time
import logging
from promt import prompt
from seleniumbase import SB
from typing import Optional
from links import links_7
from proxys import proxys_1

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(SCRIPT_DIR, "docs")
COOKIE_FILE = os.path.join(SAVE_DIR, "cookies.json")

# Создаем папку, если она не существует
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def save_cookies(sb: SB, cookie_file: str):
    """Сохраняет cookies из текущей сессии в указанный файл."""
    cookies = sb.driver.get_cookies()
    with open(cookie_file, "w", encoding="utf-8") as f:
        json.dump(cookies, f)
    logging.info(f"Cookies сохранены в {cookie_file}")


def load_cookies(sb: SB, cookie_file: str):
    """Загружает cookies из файла в сессию браузера."""
    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    for cookie in cookies:
        try:
            # Удаляем поле expiry, если оно есть, чтобы избежать ошибок
            if "expiry" in cookie:
                del cookie["expiry"]
            sb.driver.add_cookie(cookie)
        except Exception as e:
            logging.error(f"Ошибка при добавлении cookie {cookie}: {e}")
    logging.info("Cookies загружены из файла")


def manual_login(url: str):
    """
    Открывает браузер для ручного логина. У вас будет 3 минуты, чтобы авторизоваться,
    после чего cookies сохранятся и браузер закроется.
    """
    logging.info(
        "Открываем браузер для ручной авторизации. У вас есть 3 минуты для входа в систему.")
    with SB(uc=True, browser='chrome') as sb:
        sb.open(url)
        time.sleep(180)  # 3 минуты для ручного входа
        save_cookies(sb, COOKIE_FILE)
        logging.info(
            "Авторизация завершена, cookies сохранены. Браузер будет закрыт.")


class SBDriver:
    @staticmethod
    def generate_id_sequences():
        """Создает словарь, где ключ — ссылка, а значение — prompt."""
        return {link: prompt for link in links_7}

    @staticmethod
    def fetch_content(url: str):
        """
        Обрабатывает список ссылок, используя сохраненные cookies для авторизации.
        Для каждой ссылки открывается браузер с загруженными cookies, выполняется поиск и сохраняется ответ.
        """
        pending_links = SBDriver.generate_id_sequences()
        proxy_index = 0
        total_proxies = len(proxys_1)

        while pending_links:
            logging.info(f"Начинаем обработку {len(pending_links)} ссылок")
            for current_link, current_prompt in list(pending_links.items()):
                try:
                    proxy_domen = proxys_1[proxy_index]
                    proxy_index = (proxy_index + 1) % total_proxies

                    # Запускаем браузер с указанным прокси
                    with SB(uc=True, browser='chrome', proxy=0) as sb:
                        sb.open(url)

                        # Загружаем cookies, если они есть
                        if os.path.exists(COOKIE_FILE):
                            load_cookies(sb, COOKIE_FILE)
                            sb.refresh()  # Обновляем страницу для применения cookies
                        else:
                            logging.warning(
                                "Cookies отсутствуют, требуется авторизация.")
                            continue

                        sb.sleep(10)

                        # Проверяем, не произошла ли переадресация на страницу аутентификации или капчу
                        if sb.get_current_url().startswith("https://auth.openai.com/") or \
                           sb.is_element_present('iframe[src*="captcha"]'):
                            logging.warning(
                                "Обнаружена страница аутентификации или капча. Переключаем прокси...")
                            proxy_index = (proxy_index + 1) % total_proxies
                            sb.sleep(10)
                            continue

                        # Пример взаимодействия с сайтом: кликаем по кнопке, вводим запрос и отправляем его
                        button_path = '//*[@id="composer-background"]/div[2]/div[1]/div[2]/div/span/button'
                        sb.click(button_path)

                        input_area_xpath = '//*[@id="prompt-textarea"]/p'
                        cleaned_prompt = current_prompt.replace("\n", " ")
                        text_to_type = f"{current_link} {cleaned_prompt}"
                        sb.clear(input_area_xpath)
                        sb.driver.switch_to.active_element.send_keys(
                            text_to_type)

                        button_send = '//*[@id="composer-background"]/div[2]/div[2]/button'
                        sb.click(button_send)
                        sb.sleep(60)

                        # Ждем появления элемента с ответом
                        full_xpath = "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div[2]/div/div/div[2]/article[2]/div/div/div/div/div[1]/div/div/div"
                        sb.wait_for_element_visible(full_xpath, timeout=60)
                        sb.sleep(30)

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
                        if not outer_html:
                            logging.error(
                                f"Не удалось получить outerHTML для ссылки {current_link}")
                            continue

                        # Сохраняем полученный HTML в файл
                        safe_filename = "".join(
                            c for c in current_link if c.isalnum() or c in ('-', '_'))
                        output_file = os.path.join(
                            SAVE_DIR, f"{safe_filename}.html")
                        with open(output_file, "w", encoding="utf-8") as file:
                            file.write(outer_html)
                        logging.info(f"Успешно сохранен файл: {output_file}")

                        # Если все прошло успешно, удаляем ссылку из списка
                        del pending_links[current_link]

                except Exception as err:
                    logging.error(
                        f"Ошибка при обработке ссылки {current_link}: {err}")
                finally:
                    proxy_index = (proxy_index + 1) % total_proxies

                time.sleep(300)

            if pending_links:
                logging.info(
                    f"Осталось {len(pending_links)} не обработанных ссылок. Повторная попытка...")
                time.sleep(300)


if __name__ == "__main__":
    try:
        url = 'https://chatgpt.com/'
        # Если cookies отсутствуют, выполняем ручную авторизацию с 3-минутной задержкой
        if not os.path.exists(COOKIE_FILE):
            manual_login(url)
        # После авторизации или если cookies уже существуют, запускаем основной процесс
        SBDriver.fetch_content(url)
    except KeyboardInterrupt:
        pass
