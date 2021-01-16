import requests
from bs4 import BeautifulSoup
import csv
import logging

CSV = 'cards.csv'
HOST = 'https://minfin.com.ua'
URL = 'https://minfin.com.ua/cards/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
}


logging.basicConfig(filename='parser_API.log', filemode='w', level=logging.DEBUG, format='[%(levelname)s] => %(message)s')


def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='product-item')
    cards = []

    for item in items:
        cards.append(
            {
                'title': item.find('div', class_='title').get_text(strip=True),
                'link_prod': HOST + item.find('div', class_='title').find('a').get('href'),
                'brand': item.find('div', class_='brand').get_text(strip=True),
                'card_img': HOST + item.find('div', class_='image').find('img').get('src')
            }
        )
    return cards


def save_data(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Навзвание продукта', 'Ссылка', 'Бренд Банка', 'Картинка'])
        for item in items:
            writer.writerow([item['title'], item['link_prod'], item['brand'], item['card_img']])


def parser():
    page_num = input('Укажите кол-во страниц для парсинга (до 27): ')
    page_num = int(page_num.strip())
    html = get_html(URL)
    if html.status_code == 200:
        cards = []
        for page in range(1, page_num + 1):
            print(f'Парсим страничку: {page}')
            html = get_html(URL, params={'page': page})
            cards.extend(get_content(html.text))
            save_data(cards, CSV)
    else:
        print('Error')


if __name__ == '__main__':
    parser()
