import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.errors import OperationalError

# def create_connection(db_name, db_user, db_password, db_host, db_port):
#     connection = None
#     try:
#         connection = psycopg2.connect(
#             database=db_name,
#             user=db_user,
#             password=db_password,
#             host=db_host,
#             port=db_port
#         )
#         print("Соединение с базой данных успешно установлено")
#     except OperationalError as e:
#         print(f"Произошла ошибка '{e}'")
#     return connection

# # Corrected the variable assignment
# conn = create_connection(
#     "pivo_commets", "postgres", "1111", "127.0.0.1", "5432"
# )
# cursor = conn.cursor()



import requests
from bs4 import BeautifulSoup

# Функция для получения списка дорам
def get_dorama_urls(initial_page_url):
    response = requests.get(initial_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Находим все ссылки на дорамы
    dorama_links = soup.find_all('div', class_='media-heading')
    return [f"https://doramalive.ru{link.find('a')['href']}" for link in dorama_links]

# Функция для получения названия дорамы
def get_dorama_name(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_list = soup.find('ul', class_='titleList')
    return [li.text for li in title_list.find_all('li')] if title_list else []

# Функция для получения комментариев по дораме
def get_comments_for_dorama(dorama_url):
    comments = []
    
    # Добавим шаг, чтобы нажать на кнопку "Отзывы"
    response = requests.get(dorama_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    review_link = soup.find('a', {'data-type': 'review'})
    
    if review_link:
        review_url = f"https://doramalive.ru{review_link['href']}"

        while True:
            response = requests.get(review_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем блоки комментариев
            comment_blocks = soup.find_all('div', class_='item')
            
            for comment_block in comment_blocks:
                # Получаем текст комментария, если блок существует
                comment_div = comment_block.find('div', class_='fulltext detail-more')
                if comment_div:
                    comment_text = comment_div.find('p').text
                    comments.append(comment_text)
            
            # Ищем кнопку "Дальше"
            next_button = soup.find('ul', class_='pager').find('li', class_='active').find_next_sibling('li')
            
            # Если кнопка "Дальше" найдена, обновляем URL и продолжаем
            if next_button:
                review_url = f"https://doramalive.ru{next_button.find('a')['href']}"
            else:
                break

    return comments

# Пример использования
initial_page_url = "https://doramalive.ru/dorama/film/"

# Получаем список ссылок на дорамы
dorama_urls = get_dorama_urls(initial_page_url)

# Обходим каждую дораму
for dorama_url in dorama_urls:
    print(f"Обрабатывается дорама: {dorama_url}")
    
    # Получаем названия дорамы
    dorama_names = get_dorama_name(dorama_url)
    print(f"Названия дорамы: {dorama_names}")

    # Получаем комментарии для дорамы
    comments = get_comments_for_dorama(dorama_url)
    print(f"Комментарии: {comments}")
