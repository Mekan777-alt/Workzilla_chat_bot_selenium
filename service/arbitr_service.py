import time

from selenium import webdriver
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

block_ip = 'ip block'

chrome_options = Options()
chrome_options.add_argument('--start-maximized')
# chrome_options.add_argument('--window-position=0,-1500')
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
chrome_options.add_experimental_option("excludeSwitches", ['enable-logging'])
chrome_options.add_argument("--log-level=3")
# ob = Screenshot.Screenshot()

driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()

# driver.set_window_size(1920, 1080)

driver.get("https://kad.arbitr.ru/")

try:
    # cookie_disclaimer = WebDriverWait(driver, 5).until(
    #     EC.presence_of_element_located((By.ID, "sug-participants")))
    # cookie_disclaimer.click()

    element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#sug-participants textarea'))
        )
    element.send_keys("иванова евгения александровна")
    element.send_keys(Keys.ENTER)

    time.sleep(3)

    error_message_element = driver.find_elements(By.CSS_SELECTOR, '.b-page-message_error')

    if error_message_element:
        print(f'При запросе: https://kad.arbitr.ru/ произошла блокировка IP')

    time.sleep(5)

    table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "b-cases")))

    # Найти все строки в таблице
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Перебрать все строки в цикле
    for row in rows:
        # Найти все ячейки в строке
        cells = row.find_elements(By.TAG_NAME, "td")

        # Вывести текст из каждой ячейки
        for cell in cells:
            print(cell.text)
# card_elements = WebDriverWait(driver, 5).until(
#     EC.presence_of_all_elements_located((By.CLASS_NAME, "b-button")))

# for card in card_elements:
#     card.screenshot('card.png')
#     time.sleep(3)
#     card.find_element(By.CSS_SELECTOR, ".u-svg-arr-to-right").click()
#
#     driver.switch_to.window(driver.window_handles[-1])
#     time.sleep(5)
# driver.close()
# driver.switch_to.window(driver.window_handles[0])

except Exception as e:
    print(e)
finally:

    driver.close()
    driver.quit()
