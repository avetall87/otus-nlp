import random

import requests
import time
import logging

from stem import Signal
from stem.control import Controller

from crouler import get_default_headers
from stem.util.log import get_logger

from scraper.kinopoisk_scraper import parse_main_page_html, parse_category_html, parse_description_html
from dotenv import dotenv_values

logger = get_logger()
logger.propagate = False

config = dotenv_values(".env")
sleep_range_from = int(config.get("SLEEP_RANGE_FROM"))
sleep_range_to = int(config.get("SLEEP_RANGE_TO"))
tor_pass = config.get("TOR_PASS")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# У тора бывает большой таймаут при получении нового IP
def __get_rand_sleep_sec__() -> float:
    return random.randint(sleep_range_from, sleep_range_to)


def __smart_ip_request__(url):
    try:
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }

        time.sleep(__get_rand_sleep_sec__())

        with Controller.from_port(port=9051) as c:
            c.authenticate(password=tor_pass)
            c.signal(Signal.NEWNYM)
            return requests.get(url, proxies=proxies, headers=get_default_headers())

    except Exception as e:
        raise Exception('Ошибка запроса через Tor', e)


def get_main_page_metadata(url) -> [{}]:
    """
        Возвращает список категорий фильмов на кинопоиске
    """
    response = __smart_ip_request__(url)
    return parse_main_page_html(response.content)


def get_category_films(url) -> [{}]:
    """
        Возвращает список фильном в рамках категории
    """
    result = []

    page_number = 1

    while True:
        response = __smart_ip_request__(url + f'?page={page_number}')

        if response is None:
            logging.warning(f"Данные со страницы № {page_number} не получены")

        category_film_page = parse_category_html(response.content)
        if category_film_page is not None and len(category_film_page) > 0:
            logging.info(f"Данные со страницы № {page_number} получены, обрабатываю ...")
            for page in category_film_page:
                result.append(page)
            page_number = page_number + 1
        else:
            break

    return result


def get_film_description(url) -> str:
    """
        Возвращает описание фильма
    """

    response = __smart_ip_request__(url)
    film_description = parse_description_html(response.content)

    if film_description is not None:
        return film_description
    else:
        return ''
