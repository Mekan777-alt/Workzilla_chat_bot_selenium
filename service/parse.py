import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


async def check_user(fio, birthday):

    driver = webdriver.Chrome()

    driver.get("https://bankrot.fedresurs.ru")

    try:
        cookie_disclaimer = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-accept")))
        cookie_disclaimer.click()
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.ng-untouched.ng-valid.ng-dirty")))

        element.send_keys(fio)
        time.sleep(3)
        element.send_keys(Keys.ENTER)
        time.sleep(5)

        try:
            card_elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".u-card-result__wrapper")))

        except:

            return None

        for card in card_elements:
            card.screenshot(f'{birthday}.png')
            time.sleep(3)
            card.find_element(By.CSS_SELECTOR, ".u-svg-arr-to-right").click()

            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(5)
            birth_date = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".mr-3"))
            )
            date = birth_date.text

            if date == birthday:
                return True
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        return False
    except Exception as e:
        print(e)

    finally:

        driver.close()
        driver.quit()


a = check_user("Иванов Петр Иванович", "04.07.1972")
print(a)