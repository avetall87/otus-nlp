import os
import json
import logging
import csv
from dotenv import dotenv_values

from crouler.kinopoisk_crouler import get_main_page_metadata, get_category_films, get_film_description

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

config = dotenv_values(".env")
main_page_link = config.get("SEARCH_PAGE_LINK")
main_link = config.get("MAIN_LINK")
metadata_file_name = config.get("MAIN_PAGE_METADATA_FILE_NAME")
storage_name = config.get("STORAGE_NAME")
film_dataset_file_name = config.get("DATASET_FILE_NAME")

metadata_full_file_name = storage_name + '/' + metadata_file_name


def is_file_exists(file_name) -> bool:
    return os.path.isfile(file_name)


def create_storage_if_not_exist(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def load_main_page_metadata_from_file(file_name) -> [{}]:
    with open(file_name, 'r', encoding='utf8') as json_file:
        return json.load(json_file)


def save_metadata_to_file(file_name, main_page_metadata: list[{}]):
    logging.info(f"Сохраняем полученный результат в файл - {metadata_file_name}")
    with open(file_name, 'w', encoding='utf8') as file:
        file.write(json.dumps(main_page_metadata, ensure_ascii=False))


def load_film_categories(main_page_metadata) -> [{}]:
    category_len = len(main_page_metadata)

    if category_len > 0:
        logging.info(f"Получаем данные по категориям фильмов ... всего категорий {category_len}")
        for category in main_page_metadata:
            for category_name, category_metadat in category.items():
                logging.info(f"Получаем данные для категории - {category_name}")

                category_link = main_link + '/' + category_metadat['href']
                films = get_category_films(category_link)
                category[category_name]['films'] = films

                save_metadata_to_file(metadata_full_file_name, main_page_metadata)

    return main_page_metadata


def is_film_category_loaded(main_page_metadata) -> bool:
    logging.info(f"Проверяем фильмы по категориям ... ")

    result = True

    for category in main_page_metadata:
        for category_name, category_metadat in category.items():
            films = category_metadat['films']
            if films is not None and len(films) > 0:
                for film in films:
                    name = film['name']
                    link = film['link']
                    if (name is None and name == '') and (link is None or link == ''):
                        result = True
                        break
            else:
                result = False

    return result


def load_dataset_to_file(main_page_metadata):
    dataset_file_name = storage_name + '/' + film_dataset_file_name

    if is_file_exists(dataset_file_name):
        os.remove(dataset_file_name)

    dataset_header = ['name', 'link', 'year', 'country', 'rating', 'scoreCount', 'category', 'description']

    with open(storage_name + '/' + film_dataset_file_name, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(dataset_header)

        for category in main_page_metadata:
            for category_name, category_metadat in category.items():
                for film in category_metadat['films']:
                    logging.info(f"Получаем описание фильма - {film['name']}")

                    film['category'] = category_name
                    film['description'] = get_film_description(main_link + film['link'])

                    writer.writerow([
                        film['name'],
                        film['link'],
                        film['year'],
                        film['country'],
                        film['rating'],
                        film['scoreCount'],
                        film['category'],
                        film['description']
                    ])

                    f.flush()


def main():
    logging.info(f"Я запустился и начал работу ... создам хранилище если его еще нету - {storage_name}")
    create_storage_if_not_exist(storage_name)

    if not is_file_exists(metadata_full_file_name):
        logging.info(f"Получаем метаданные главной страницы Кинопоиска - {main_page_link}")
        main_page_metadata = get_main_page_metadata(main_page_link)

        save_metadata_to_file(metadata_full_file_name, main_page_metadata)
    else:
        logging.info(
            f"Метаданные главной страницы Кинопоиска {main_page_link} были загружены ранее - {metadata_full_file_name}")

        logging.info(f"Считаем данные из файла ... ")
        main_page_metadata = load_main_page_metadata_from_file(metadata_full_file_name)

        if not is_film_category_loaded(main_page_metadata):
            main_page_metadata = load_film_categories(main_page_metadata)

        load_dataset_to_file(main_page_metadata)


if __name__ == '__main__':
    main()
