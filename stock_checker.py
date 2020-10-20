from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException, \
    ElementClickInterceptedException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import yagmail
import pathlib
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging
import json
import uuid
from webdriver_manager.firefox import GeckoDriverManager
from settings.setting import PUSH_API_TOKEN, RECEIVER_NO, SENDER_NO, DEVICE_ID, RECEIVER_EMAIL, RECEIVER_EMAIL2


def notify_me(product, website_url, screenshot):
    logging.info('Notifying user')
    sender_email = RECEIVER_EMAIL
    receiver_email = RECEIVER_EMAIL
    if 'juicy' in website_url or 'weekday' in website_url:
        receiver_two = RECEIVER_EMAIL2
    subject = "Product %s now in stock" % product

    yag = yagmail.SMTP(user=sender_email, password="khbdkwxyidrdhuw")
    logging.info('Mail ready to send')
    contents = [
        "Product now in stock", screenshot,
        "\nGet this product at %s" % website_url
    ]

    try:
        yag.send(to=[receiver_email, receiver_two], subject=subject, contents=contents)
    except Exception as e:
        logging.info('Exception occurred %s' % e)

    dev_id = DEVICE_ID
    message_body = "Product now in stock at %s" % website_url
    payload = {
        "data": {"addresses": [SENDER_NO], "guid": str(uuid.uuid4()).replace("-", ""), "message": message_body,
                 "target_device_iden": dev_id}}
    if 'tala' in website_url or 'weekday' in website_url:
        payload['data']['addresses'].clear()
        payload['data']['addresses'].append(RECEIVER_NO)
    headers = {'Access-Token': PUSH_API_TOKEN, 'Content-Type': 'application/json'}
    logging.info(requests.get('https://api.pushbullet.com/v2/devices', headers=headers).text)
    logging.info(requests.get('https://api.pushbullet.com/v2/users/me', headers=headers).text)
    logging.info(requests.post('https://api.pushbullet.com/v2/texts', headers=headers, data=json.dumps(payload)).text)


def check_levis():
    base_url = 'https://www.levi.com/GB/en_GB/men/511-slim-jeans-short/p/'
    product_code = 365550202
    options = Options()
    options.add_argument('--headless')
    driver = Firefox(options=options)
    file_name = 'screenshot_%s.png' % (datetime.now().date())
    screenshot_file_path = pathlib.WindowsPath(pathlib.Path(__file__).parent, 'output', file_name)
    full_url = base_url + str(product_code)
    logging.info("Checking stock at %s" % full_url)
    try:
        driver.get(full_url)
        try:
            element_present = EC.element_to_be_clickable((By.CSS_SELECTOR, 'form#addToCartForm > button'))
            WebDriverWait(driver, 10).until(element_present)
        except TimeoutException:
            logging.debug("Timed out element not clickable")
            pathlib.Path.mkdir(pathlib.Path(__file__).parent / 'output', exist_ok=True, parents=True)
            driver.get_screenshot_as_file(str(screenshot_file_path))
            logging.info("Screenshot saved to %s" % str(screenshot_file_path))

        if driver.find_element_by_css_selector("form#addToCartForm > button").is_displayed():
            logging.info('Levis 511 slim shorts (%s) are out of stock' % str(product_code))
        else:
            logging.info('Levis 511 slim shorts (%s) are now in stock!' % str(product_code))
            logging.debug(driver.find_element_by_css_selector("form#addToCartForm > button").get_attribute("style"))
            notify_me(product_code, full_url, str(screenshot_file_path))
    except WebDriverException:
        logging.info("There has been an error with connecting to the url", exc_info=True)
        logging.error("error", exc_info=True)
    driver.close()


def check_tala_stock():
    base_url = 'https://www.wearetala.com/products/the-zinnia-legging-black'
    product_code = 19731513671776
    full_url = '%s?variant=%s' % (base_url, product_code)
    logging.info("Checking stock at %s" % full_url)
    sauce = requests.get(full_url).text
    soup = BeautifulSoup(sauce, 'lxml')
    stock = soup.find("button", {"id": "AddToCart-product-template"}).text
    if "sold out" in stock.lower():
        logging.info("leggings %s" % stock.lower().strip())
    else:
        logging.info("leggings in stock %s" % stock.lower().strip())
        notify_me(product_code, full_url, "no screenshot")


def check_weekday_stock(product_code):
    base_url = 'https://www.weekday.com/en_gbp/men/hoodies-sweatshirts/'
    full_url = '%s%s' % (base_url, product_code)
    logging.info("Checking stock at %s" % full_url)
    options = Options()
    options.add_argument('--headless')
    driver = Firefox(options=options)
    driver.get(full_url)
    i = 0
    item = None
    while i < 100:
        try:
            item = driver.find_element_by_css_selector("button#addToBagButton")
        except:
            break
        i += 1
    try:
        if item.is_displayed() and len(item.text) > 5:
            logging.info("%s in stock" % product_code)
            notify_me(product_code, full_url, "no screenshot")
        else:
            logging.info("%s not in stock" % product_code)
    except (NoSuchElementException, AttributeError):
        logging.info("%s not in stock" % product_code)


def check_urban_stock(size_code, product_url):
    logging.info('SIZE CODES 1:XS 2:S 3:M 4:L')
    size_code_catalog = {
        1: 'XS',
        2: 'S',
        3: 'M',
        4: 'L'
    }
    try:
        logging.info('Selected size %s' % size_code_catalog[size_code])
    except KeyError:
        logging.info('%s is not a valid size' % size_code)
        return
    base_url = product_url
    pathlib.Path.mkdir(pathlib.Path(__file__).parent / 'output', exist_ok=True, parents=True)
    try:
        options = Options()
        options.add_argument('--headless')
        driver = Firefox(executable_path=GeckoDriverManager().install(), options=options)
        driver.get(base_url)
        logging.info('Browser opened successfully at %s' % base_url)
    except Exception as e:
        logging.info('Exception occured %s' % e)
    file_name = 'screenshot_%s.png' % (datetime.now().date())
    screenshot_file_path = pathlib.PurePosixPath(pathlib.Path(__file__).parent, 'output', file_name)
    assert "Juicy" in driver.title
    wait_time = 0
    item = None
    while wait_time < 500:
        try:
            item = driver.find_element_by_css_selector(
                "li.c-pwa-radio-boxes__item--default:nth-child(%d) > label:nth-child(2)" % size_code)
        except:
            logging.info('Could not find item')
            break
        wait_time += 1
    try:
        driver.get_screenshot_as_file(str(screenshot_file_path))
        logging.info("Screenshot saved to %s" % str(screenshot_file_path))
        try:
            item.click()
            logging.info("%s in stock" % item.text)
            notify_me("Juicy", base_url, str(screenshot_file_path))
        except ElementClickInterceptedException as e:
            logging.info(e.msg)
            logging.info("%s not in stock" % item.text)
    except (NoSuchElementException, AttributeError):
        logging.info("%s not in stock" % 'Juicy')

    driver.quit()


def main():
    logging.basicConfig(
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[logging.FileHandler(str(pathlib.Path(pathlib.Path(__file__).parent, 'app.log'))),
                  logging.StreamHandler()]
    )
    logging.info('Started')
    # check_levis()
    # check_tala_stock()
    # check_weekday_stock('product.paris-sweatshirt-purple.0410408022.html')
    # check_weekday_stock('product.willy-sweatshirt-black.0850915001.html')
    check_urban_stock(1,
                      'https://www.urbanoutfitters.com/en-gb/shop/juicy-couture-uo-exclusive-blue-flared-track-pants')
    logging.info("Log file in %s" % str(pathlib.Path(pathlib.Path(__file__).parent, 'app.log')))


if __name__ == '__main__':
    main()
    logging.info('Finished')
