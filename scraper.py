import os
import scrapy
from bs4 import BeautifulSoup
from langdetect import detect
from urllib.parse import urljoin
from scrapy.crawler import CrawlerProcess

PAGES_COUNT = 100

SAVE_DIR = 'pages'
INDEX_FILE = 'index.txt'
DUMP_FILE = 'выкачка.txt'

RESTRICTED_DOMAINS = [
    't.me', 'instagram.com', 'vk.com', 'm.vk.com', 'ok.ru', 'youtube.com',
    'www.youtube.com', 'www.tiktok.com', 'viber.com', 'music.apple.com', 'rutube.ru',
    'www.linkedin.com', 'linkedin.com', 'apps.apple.com', 'www.apple.com', 'github.com',
    'account.ncbi.nlm.nih.gov', 'kudago.com', 'www.zoom.com'
]

RESTRICTED_URLS = [
    'https://zen.yandex.ru/tolkosprosit',
]

START_URLS = [
    'https://elementy.ru/',
    'https://nauka.tass.ru/',
    'https://nplus1.ru/',
    'https://postnauka.ru/',
    'https://www.nkj.ru/',
    'https://indicator.ru/',
    'https://chrdk.ru/',
    'https://scientificrussia.ru/',
    'https://kot.sh/',
    'https://22century.ru/'
]

TEXT_FILE_EXTENSIONS = ['.html', '.htm', '', '/']

visited_urls = set()


def extract_text_from_html(html):
    """
    Извлекает текст из HTML,
    удаляя теги и оставляя только чистый текст
    """
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def is_correct_language(text, expected_lang="ru"):
    """
    Определяет язык текста после очистки HTML
    """
    try:
        clean_text = extract_text_from_html(text)
        lang = detect(clean_text)
        return lang == expected_lang
    except:
        return False


class Scraper(scrapy.Spider):
    name = "pages"
    start_urls = START_URLS
    page_counter = 0

    def parse(self, response):
        global visited_urls

        # Фильтрация запрещенных доменов и ссылок
        if response.url in RESTRICTED_URLS or any(domain in response.url for domain in RESTRICTED_DOMAINS):
            self.log(f'Skipping blocked URL: {response.url}')
            return

        # Проверка, что страница содержит текстовый контент
        if not self.is_text_page(response.url):
            self.log(f'Skipping non-text page: {response.url}')
            return

        # Проверка на дубликаты
        if response.url in visited_urls:
            self.log(f'Skipping duplicate URL: {response.url}')
            return
        visited_urls.add(response.url)

        # Извлекаем текст из HTML
        text_content = extract_text_from_html(response.text)

        # Проверка языка (оставляем только русские страницы)
        if not is_correct_language(response.text, "ru"):
            self.log(f'Skipping {response.url} - incorrect language')
            return

        # Генерация имени файла
        self.page_counter += 1
        filename = f'{self.page_counter}-{response.url.split("/")[-2]}.html'
        filepath = os.path.join(SAVE_DIR, filename)

        # Сохранение HTML-контента страницы
        with open(filepath, 'wb') as f:
            f.write(response.body)

        # Добавление в индекс
        with open(INDEX_FILE, 'a') as f:
            f.write(f'{self.page_counter},{response.url}\n')

        # Запись в общий файл выкачки
        with open(DUMP_FILE, 'a', encoding='utf-8') as f:
            f.write(f'FILE {self.page_counter}: {response.url}\n')
            f.write(response.text + '\n' + '=' * 80 + '\n')

        self.log(f'Saved file {filename}. Total received: {self.page_counter} pages')

        # Остановка, если достигли лимита
        if self.page_counter >= PAGES_COUNT:
            self.log(f'Reached {PAGES_COUNT} pages. Stopping crawler!')
            raise scrapy.exceptions.CloseSpider('Reached page limit')

        # Сбор ссылок на новые страницы
        next_pages = set(response.css('a::attr(href)').getall() + response.xpath("//a/@href").getall())
        next_pages = set(urljoin(response.url, link) for link in next_pages)

        for next_page in next_pages:
            if next_page and self.page_allowed(next_page):
                yield response.follow(next_page, callback=self.parse)

    def page_allowed(self, url):
        """
        Проверяет, можно ли посещать страницу
        """
        try:
            url_domain = url.split('/')[2]
            if url in RESTRICTED_URLS or url_domain in RESTRICTED_DOMAINS:
                self.log(f'Skipping restricted URL before visiting: {url}')
                return False
            if url in visited_urls:
                return False
        except:
            pass
        return True

    def is_text_page(self, url):
        """
        Проверяет, является ли страница текстовой
        (не JS, CSS, PDF и т. д.)
        """
        return any(url.endswith(ext) for ext in TEXT_FILE_EXTENSIONS)


def create_directory():
    """
    Создает папку для сохранения данных,
    если её нет
    """
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


if __name__ == "__main__":
    create_directory()
    process = CrawlerProcess()
    process.crawl(Scraper)
    process.start()
