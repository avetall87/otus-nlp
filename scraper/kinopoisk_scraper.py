from bs4 import BeautifulSoup
import re
import logging

from stem.util.log import get_logger

logger = get_logger()
logger.propagate = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def parse_main_page_html(html) -> [{}]:
    soup = BeautifulSoup(html, 'html.parser')

    result = []

    a_list = soup.findAll('a', attrs={'class': 'styles_root__c9qje'})
    try:
        for element in a_list:
            e_metadata = __get_main_page_element_metadata__(element)
            if e_metadata is not None and len(e_metadata) > 0:
                result.append(e_metadata)
        return result
    except Exception as e:
        logging.error('Ошибка при разборе html - разбор базовой страницы Кинопоиска - %s', e)
    return result


def parse_category_html(html) -> [{}]:
    soup = BeautifulSoup(html, 'html.parser')

    result = []

    a_list = soup.findAll('div', attrs={'class': 'styles_root__ti07r'})
    try:
        for element in a_list:
            e_metadata = __get_category_element_metadata__(element)
            if e_metadata is not None and len(e_metadata) > 0:
                result.append(e_metadata)
        return result
    except Exception as e:
        logging.error('Ошибка при разборе html - разбор базовой страницы Кинопоиска - %s', e, e.__traceback__)
    return result


def parse_description_html(html) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    description_list = []

    descriptions = soup.findAll('p', attrs={'class': 'styles_paragraph__wEGPz'})

    try:
        for description in descriptions:
            description_list.append(description.text)

        return '\n'.join(description_list).replace(' ', ' ')

    except Exception as e:
        logging.error('Ошибка при разборе html - разбор базовой страницы Кинопоиска - %s', e, e.__traceback__)
    return ''


def __get_category_element_metadata__(element) -> {}:
    result = {}
    try:
        if element is not None:
            soup = BeautifulSoup(str(element), 'html.parser')

            name = soup.find('span', attrs={'class': 'styles_mainTitle__IFQyZ styles_activeMovieTittle__kJdJj'}).text
            link = soup.find('a', attrs={'class': 'styles_root__wgbNq'}).attrs['href']
            year = soup.find('span', attrs={'class': 'desktop-list-main-info_secondaryText__M_aus'}).text

            if year is not None and year != '':
                year = re.search('(\\d{4})', year).group()

            country = soup.find('span', attrs={'class': 'desktop-list-main-info_truncatedText__IMQRP'}).text

            if country is not None and country != '':
                split_result = country.split(' • ')
                if len(split_result) > 1:
                    country = split_result[0]

            rating = soup.find('span',
                               attrs={'class': 'styles_kinopoiskValuePositive__vOb2E styles_kinopoiskValue__9qXjg'})

            if rating is not None:
                rating = soup.find('span',
                                   attrs={
                                       'class': 'styles_kinopoiskValuePositive__vOb2E styles_kinopoiskValue__9qXjg'}) \
                    .text
            else:
                rating = soup.find('span',
                                   attrs={
                                       'class': 'styles_kinopoiskValueNeutral__sW9QT styles_kinopoiskValue__9qXjg'})
                if rating is not None:
                    rating = rating.text
                else:
                    rating = ''

            score_count = soup.find('span', attrs={'class': 'styles_kinopoiskCount__2_VPQ'})

            if score_count is not None:
                score_count = soup.find('span', attrs={'class': 'styles_kinopoiskCount__2_VPQ'}).text
            else:
                score_count = ''

            result = {'name': name,
                      'link': link.replace(' ', ' '),
                      'year': year.replace(' ', ' '),
                      'country': country.replace(' ', ' '),
                      'rating': rating,
                      'scoreCount': score_count}
        return result
    except Exception as e:
        logging.error('Не получилось получить метаданные для элемента - %s \n %s', element, e, e.__traceback__)
        return result


def __get_main_page_element_metadata__(element) -> {}:
    result = {}
    try:
        if element is not None:
            film_count_str = element.next.next.next.next.next_sibling.text
            re_film_count = re.sub(r'\s\w+', '', re.match('^[0-9]', film_count_str).string)
            result = {
                element.next.next.next.next.next.text: {'href': element.attrs['href'], 'filmCount': re_film_count}}
        return result
    except Exception as e:
        logging.warning('Не получилось получить метаданные для элемента - %s \n %s', element, e)
        return result
