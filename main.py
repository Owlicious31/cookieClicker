import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

LOADING_TIME: int = 6
game_running: bool = True
clicker_check_time: float = time.time() + 5
game_check_time: float = time.time() + 60 * 5

logging.basicConfig(level=logging.INFO,format="%(filename)s - %(levelname)s - %(message)s - %(asctime)s")


def click_on_language(loading_time: int, lang: str, web_driver: WebDriver) -> None:
    """
    Select a language on the cookie clicker start screen.
    :param loading_time: Time to wait before and after selecting the language to allow the page to load fully.
    :param lang: The language code of the language being selected.
    :param web_driver: A Selenium Chrome webdriver.
    :return: None
    """
    language_options: list[str] = ["EN","FR","DE","NL","CS","PL","IT","PT","ES","JA","ZH","KO","RU"]

    time.sleep(loading_time)

    if lang.upper() not in language_options:
        logging.error("Unrecognized language")
        raise Exception(f"Unrecognized language supported languages are: {language_options}")

    language_choice: WebElement = web_driver.find_element(By.CSS_SELECTOR, f"#langSelect-{lang.upper()}")
    language_choice.click()

    logging.info(f"Selected language: {lang}")

    time.sleep(loading_time)


def click_on_cookie(web_driver: WebDriver) -> None:
    """
    Click on the cookie.
    Once 5 seconds have passed since the game start the function will call the check_upgrades function.
    :param web_driver: A Selenium Chrome webdriver.
    :return: None
    """
    global clicker_check_time

    cookie: WebElement = web_driver.find_element(By.ID,"bigCookie")
    cookie.click()

    current_time: float = time.time()

    if current_time > clicker_check_time:
        clicker_check_time = current_time + 5
        check_upgrades(web_driver=web_driver)


def check_upgrades(web_driver: WebDriver) -> None:
    """
    Retrieve the prices of all available store prices and buy them if the current number of cookies
    is larger than the price.
    :param web_driver: A Selenium Chrome webdriver.
    :return: None
    """
    logging.info("Checking upgrades")

    store_price_elements: list[WebElement] = web_driver.find_elements(By.CSS_SELECTOR,"#products .content .price")
    store_prices: list[int] = [int("".join(price.text.split(sep=","))) for price in store_price_elements if price.text]

    logging.info(f"Store prices: {store_prices}")

    cookie_label: WebElement = web_driver.find_element(By.CSS_SELECTOR,"#cookies")
    current_num_cookies: int = int("".join(cookie_label.text.split(sep=" ")[0].split(sep=",")))

    logging.info(f"Current num of cookies:{current_num_cookies}")

    for price in store_prices:
        if current_num_cookies >= price:
            logging.info("Buying upgrade")

            store_upgrades: list[WebElement] = web_driver.find_elements(By.CSS_SELECTOR, "#products div")
            store_upgrades = [upgrade for upgrade in store_upgrades if "product unlocked" in upgrade.get_attribute("class")]

            logging.info(f"Store upgrades: {store_upgrades}")

            selected_upgrade_num: int = store_prices.index(price)
            selected_upgrade: WebElement = store_upgrades[selected_upgrade_num]

            web_driver.execute_script("arguments[0].click();",selected_upgrade)

            logging.info("Bought upgrade")


chrome_options: webdriver.ChromeOptions = webdriver.ChromeOptions()
chrome_options.add_experimental_option(name="detach",value=True)

driver: WebDriver = webdriver.Chrome(options=chrome_options)

driver.get("https://orteil.dashnet.org/cookieclicker/")

click_on_language(lang="EN", loading_time=LOADING_TIME, web_driver=driver)
logging.info("Game started.")


while game_running:
    click_on_cookie(web_driver=driver)
    time_now: float = time.time()

    if time_now > game_check_time:
        cookies: WebElement = driver.find_element(By.CSS_SELECTOR, "#cookies")
        cookies_per_second: str = cookies.text.split(sep=" ")[-1]

        logging.info(f"Cookies per second: {cookies_per_second}")

        game_check_time = time_now + 60 * 5

driver.quit()