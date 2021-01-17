import requests
from bs4 import BeautifulSoup
import csv
import logging

CSV_FILE = 'game.csv'
HOST = 'https://stopgame.ru'
URL = 'https://stopgame.ru/games/'
HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
}


logging.basicConfig(filename='parser_API.log', filemode='w', level=logging.DEBUG,
                    format='[%(levelname)s] => %(message)s')


def get_html(url, params=''):
    req = requests.get(url, headers=HEADERS, params=params)
    return req


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='item game-summary game-summary-horiz')
    games = []
    for item in items:
        details = item.find_all('div', class_='game-spec')
        tmp = dict(
            {
                'title': item.find('div', class_='caption caption-bold').get_text(strip=True),
                'link': HOST + item.find('div', class_='caption caption-bold').find('a').get('href'),
                'img': item.find('div', class_='image').get('style'),
                'platform': details[0].find('span', class_='value').get_text(),
                'genre': details[1].find('span', class_='value').get_text(),
                'date': details[2].find('span', class_='value').get_text()
            }
        )
        tmp = get_clear_link(tmp)
        games.append(tmp)
    return games


def get_clear_link(dictionary):
    for key, value in dictionary.items():
        if key.find('img') != -1:
            i_beg = value.find('url(')
            i_end_jpg = value.rfind('jpg')
            i_end_jpeg = value.rfind('jpeg')
            i_end_png = value.rfind('png')
            if i_beg != -1 & (i_end_jpg != -1 | i_end_jpeg != -1 | i_end_png != -1):
                if i_end_jpg != -1:
                    dictionary.update({'img': value[i_beg + 4: i_end_jpg + 3]})
                elif i_end_png != -1:
                    dictionary.update({'img': value[i_beg + 4: i_end_png + 3]})
                else:
                    dictionary.update({'img': value[i_beg + 4: i_end_jpeg + 4]})
    return dictionary


def save_data(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Навзвание продукта', 'Ссылка', 'Превьюшка', 'Платформа', 'Жанр', 'Дата выхода'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['img'], item['platform'], item['genre'], item['date']])


def parser():
    page_num = input('Укажите кол-во страниц для парсинга (до 18): ')
    page_num = int(page_num.strip())
    html = get_html(URL)
    if html.status_code == 200:
        games = []
        for page in range(1, page_num + 1):
            print(f'Парсим страничку: {page}')
            html = get_html(URL, params={'p': page})
            games.extend(get_content(html.text))
            save_data(games, CSV_FILE)
        print('Парсинг окончен')
    else:
        print('Error')


if __name__ == '__main__':
    parser()
