from selenium import webdriver
import json
import time
import requests
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import os
from config import Config


class Scraper:
    count = 0

    def __init__(self):
        self.browser = self.brows()

    def brows(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            # "download.default_directory": Config.path_to_pdf_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
        })
        # options.add_argument('--headless')  # для открытия headless-браузера
        return webdriver.Chrome(executable_path=Config.path_to_chromedriver,
                                options=options)

    def auth(self):
        self.browser.get('https://github.com/login')
        self.browser.find_element_by_id('login_field').send_keys(Config.login)
        self.browser.find_element_by_id('password').send_keys(Config.password)
        time.sleep(4)
        self.browser.find_element_by_css_selector('input[type="submit"]').click()
        time.sleep(5)

    # Бегает по страницам пагинации, переходит по ссылкам и проваливается глубже
    def get_main_page(self):
        num_page = 1
        while True:
            if num_page > Config.max_page:
                print(f"get_base_page:Exiting.")
                break
            self.browser.get(
                f'https://github.com/search?p={num_page}&q={query}+&type=Repositories')
            print('page : ' + str(num_page))
            time.sleep(2)
            try:
                num_page += 1
                yield
                time.sleep(2)
            except NoSuchElementException:
                print(f"get_base_page:Exiting.")
                break

    def get_one_list_page(self):
        soup = BeautifulSoup(self.browser.page_source, 'lxml')
        try:  # TODO вот тут искать элемент в котором ссылка на целевую страницу
            list_users = soup.find('ul', class_='repo-list').find_all('li')

            for row in list_users:
                row = row.find('a', class_='v-align-middle')
                link = row.get('href').split('/')[1]
                yield self.get_page(link, self.browser)
        except AttributeError:
            print('ошибка')
            yield 'empty'

    def get_page(self, row, browser):
        url_one_res = row
        browser.get('https://github.com/' + url_one_res)
        try:
            return self.get_data(url_one_res)
        except AttributeError:
            pass

    # Получение данных из html кода
    def get_data(self):
        pass

    def post_to_server(self, data):
        self.count += 1
        print('отправляю на сервер чувака номер', self.count)
        response = requests.post(Config.endpoint, data=data.encode('utf8'))
        print(f'Response: {response.text}')
