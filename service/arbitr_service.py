import os
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import uuid

list_image = []


def check_table(fio):
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ['enable-logging'])
    chrome_options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=chrome_options)

    driver.set_window_size(1920, 1080)

    driver.get("https://kad.arbitr.ru/")

    try:

        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#sug-participants textarea'))
        )
        check_human = fio
        check_human.lower()
        element.send_keys(check_human)
        element.send_keys(Keys.ENTER)

        time.sleep(3)

        error_message_element = driver.find_elements(By.CSS_SELECTOR, '.b-page-message_error')

        if error_message_element:
            return None

        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.bankruptcy'))
        )

        button.click()
        random_uuid = uuid.uuid4()
        time.sleep(10)
        driver.save_screenshot(f'{os.getcwd()}/files/{random_uuid}-{check_human.upper()}.png')
        list_image.append(f'{os.getcwd()}/files/{random_uuid}-{check_human.upper()}.png')

        time.sleep(5)

        table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "b-cases")))

        rows = table.find_elements(By.TAG_NAME, "tr")

        # Перебрать все строки в цикле
        for row in rows:
            # Найти все ячейки в строке
            cells = row.find_elements(By.TAG_NAME, "td")

            if cells[2].text.lower() == check_human or cells[3].text.lower() == check_human:

                return True

        return False

    except Exception as e:
        return e

    finally:

        driver.close()
        driver.quit()
