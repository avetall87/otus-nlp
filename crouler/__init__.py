# какая-то иницифализация
from fake_useragent import UserAgent


def get_default_headers() -> {}:
    return {'User-Agent': UserAgent().random}
