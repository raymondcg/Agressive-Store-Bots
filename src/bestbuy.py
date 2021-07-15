import bs4
import sys
import time
import yaml
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException, \
    WebDriverException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

formatTimeString = "%m/%d/%Y %H:%M:%S"

# Further instructions in 'example_config.yml' for how to create your own config.yml file. It is done this way to ensure that the configuration file is never uploaded to the internet.
with open('../config/config.yml', 'r') as file:
    configuration_file = yaml.safe_load(file)

# 1. General Settings
test_mode = configuration_file["test_mode"]
headless_mode = configuration_file["headless_mode"]
webpage_refresh_timer = configuration_file["webpage_refresh_timer"]

# 2. Product URLs
url = configuration_file["product"]


# 3. Firefox Profile
def create_driver():
    """Creating firefox driver to control webpage. Please add your firefox profile down below."""
    options = Options()
    options.headless = headless_mode
    profile = webdriver.FirefoxProfile(configuration_file["firefox_profile"])
    web_driver = webdriver.Firefox(profile, options=options, executable_path=GeckoDriverManager().install())
    web_driver.set_window_size(960, 900)
    return web_driver


# 4. credit card CVV Number
CVV = configuration_file["cvv"]


# 5. Twilio Account
toNumber = configuration_file["twilio"]["toNumber"]
fromNumber = configuration_file["twilio"]["fromNumber"]
accountSid = configuration_file["twilio"]["accountSid"]
authToken = configuration_file["twilio"]["authToken"]
client = Client(accountSid, authToken)


# ----------------------------------------------------------------------------------------------------------------------


def time_sleep(x, driver):
    """Sleep timer for page refresh."""
    for i in range(x, -1, -1):
        time1 = datetime.now().strftime(formatTimeString)
        print(f"{time1} Monitoring Page. Refreshing in {i} seconds")
        time.sleep(1)
    driver.execute_script('window.localStorage.clear();')
    driver.refresh()


def extract_page(driver):
    """bs4 page parser."""
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def driver_click(driver, find_type, selector):
    """Driver Wait and Click Settings."""
    while True:
        if find_type == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)
        elif find_type == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)
        elif find_type == 'xpath':
            try:
                driver.find_element_by_xpath(f"//*[@class='{selector}']").click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)


def searching_for_product(driver):
    """Scanning for product."""
    driver.get(url)

    print("\nWelcome To Bestbuy Bot! Join The Discord To find out What Week Bestbuy drops GPU's and Consoles!")
    print("Discord: https://discord.gg/qQDvwT6q3e")
    print("Donations keep the script updated!\n")
    print("Cashapp Donation: $TreborNamor")
    print("Bitcoin Donation: 16JRvDjqc1HrdCQu8NRVNoEjzvcgNtf6zW ")
    print("Dogecoin Donation: DSdN7qR1QR5VjvR1Ktwb7x4reg7ZeiSyhi \n")
    print("Bot deployed!\n")

    while True:
        soup = extract_page(driver)
        wait = WebDriverWait(driver, 15)
        wait2 = WebDriverWait(driver, 5)

        try:
            add_to_cart_button = soup.find('button', {
                'class': 'btn btn-primary btn-lg btn-block btn-leading-ficon add-to-cart-button'})

            if add_to_cart_button:
                print(f'Add To Cart Button Found!')

                # Queue System Logic.
                try:
                    # Entering Queue: Clicking "add to cart" 2nd time to enter queue.
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
                    driver_click(driver, 'css', '.add-to-cart-button')
                    print("Clicked Add to Cart Button. Now sending message to your phone.")
                    print("You are now added to Best Buy's Queue System. Page will be refreshing. Please be patient. It could take a few minutes.\n")

                    # Sleep timer is here to give Please Wait Button to appear. Please don't edit this.
                    time.sleep(5)
                    driver.refresh()
                    time.sleep(5)
                except (NoSuchElementException, TimeoutException) as error:
                    print(f'Queue System Error: ${error}')

                # Sending Text Message To let you know you are in the queue system.
                try:
                    client.messages.create(to=toNumber, from_=fromNumber,
                                           body=f'Your In Queue System on Bestbuy! {url}')
                except (NameError, TwilioRestException):
                    pass

                # In queue, just waiting for "add to cart" button to turn clickable again.
                # page refresh every 15 seconds until Add to Cart button reappears.
                # Don't worry about people saying you'll losing your space in line if you refresh page.
                # I've tested this bot plenty times and it is not true. You can test the bot to find out.
                # When bot clicks "Add to Cart" button, a request is sent to server, and server is just waiting for a response.
                # No possible way to lose your spot once request is sent.
                while True:
                    try:
                        add_to_cart = driver.find_element_by_css_selector(".add-to-cart-button")
                        please_wait_enabled = add_to_cart.get_attribute('aria-describedby')

                        if please_wait_enabled:
                            driver.refresh()
                            time.sleep(15)
                        else:  # When Add to Cart appears. This will click button.
                            print("Add To Cart Button Clicked A Second Time.\n")
                            wait2.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".add-to-cart-button")))
                            time.sleep(2)
                            driver_click(driver, 'css', '.add-to-cart-button')
                            time.sleep(2)
                            break
                    except(NoSuchElementException, TimeoutException) as error:
                        print(f'Queue System Refresh Error: ${error}')

                # Going To Cart Process.
                driver.get('https://www.bestbuy.com/cart')

                # Checking if item is still in cart.
                try:
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary']")))
                    time.sleep(1)
                    driver_click(driver, 'xpath', 'btn btn-lg btn-block btn-primary')
                    print("Item Is Still In Cart.")
                except (NoSuchElementException, TimeoutException):
                    print("Item is not in cart anymore. Retrying..")
                    time_sleep(3, driver)
                    searching_for_product(driver)

                # Logging Into Account.
                print("\nAttempting to Login. Firefox should remember your login info to auto login.")
                print("If you're having trouble with auto login. Close all firefox windows.")
                print("Open firefox manually, and go to bestbuy's website. While Sign in, make sure to click 'Keep Me Logged In' button.")
                print("Then run bot again.\n")

                # Click Shipping Option. (if available)
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary button__fast-track']")))
                    time.sleep(2)
                    shipping_class = driver.find_element_by_xpath("//*[@class='ispu-card__switch']")
                    shipping_class.click()
                    print("Clicking Shipping Option.")
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException) as error:
                    print(f'shipping error: {error}')

                # Trying CVV
                try:
                    print("\nTrying CVV Number.\n")
                    wait2.until(EC.presence_of_element_located((By.ID, "credit-card-cvv")))
                    time.sleep(1)
                    security_code = driver.find_element_by_id("credit-card-cvv")
                    time.sleep(1)
                    security_code.send_keys(CVV)
                except (NoSuchElementException, TimeoutException):
                    pass

                # Final Checkout.
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary button__fast-track']")))
                    # comment the one down below. vv
                    if not test_mode:
                        print("Product Checkout Completed.")
                        driver_click(driver, 'xpath', 'btn btn-lg btn-block btn-primary button__fast-track')
                    if test_mode:
                        print("Test Mode - Product Checkout Completed.")
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
                    print("Could Not Complete Checkout.")

                # Completed Checkout.
                print('Order Placed!')
                time.sleep(1800)
                driver.quit()

        except (NoSuchElementException, TimeoutException) as error:
            print(f'error is: {error}')

        time_sleep(webpage_refresh_timer, driver)


def run():
    print("Starting purchaser")
    driver = create_driver()
    try:
        searching_for_product(driver)
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)
    print("Purchaser complete!")


if __name__ == '__main__':
    run()
