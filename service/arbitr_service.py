import time

from selenium import webdriver
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()

driver.get("https://kad.arbitr.ru/")

try:
    # cookie_disclaimer = WebDriverWait(driver, 5).until(
    #     EC.presence_of_element_located((By.ID, "sug-participants")))
    # cookie_disclaimer.click()

    element = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#sug-participants > div > textarea")))

    element.send_keys("иванова евгения александровна")
    element.send_keys(Keys.ENTER)

    button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[alt='Найти'][type='submit']")))


    button.click()

    time.sleep(3)

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
