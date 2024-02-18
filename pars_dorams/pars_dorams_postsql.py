import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import Json
from psycopg2.errors import OperationalError

base_url = 'https://doramalive.ru/dorama/film/'
current_page = 1  # начинаем с первой страницы

def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        print("Соединение с базой данных успешно установлено")
    except OperationalError as e:
        print(f"Произошла ошибка '{e}'")
    return connection

# Corrected the variable assignment
conn = create_connection(
    "pivo_commets", "postgres", "1111", "127.0.0.1", "5432"
)
cursor = conn.cursor()

while True:
    # Формируем URL текущей страницы
    current_page_url = f"{base_url}?PAGEN_1={current_page}"

    # Отправка запроса на страницу и получение HTML-кода
    response = requests.get(current_page_url)
    if response.status_code == 200:
        html = response.text

        # Парсинг HTML текущей страницы
        soup = BeautifulSoup(html, 'html.parser')

        # Находим все элементы с классом 'media-heading'
        media_headings = soup.find_all('div', class_='media-heading')

        # Проходим циклом по каждому элементу
        for media_heading in media_headings:
            # Извлекаем информацию из каждого элемента
            title = media_heading['title'] if 'title' in media_heading.attrs else "Нет информации о названии"
            href = media_heading.a['href']

            print(f"Title: {title}")
            print(f"Href: {href}")

            # Проверяем, что у нас есть название дорамы для продолжения
            if title == "Нет информации о названии":
                print("Название дорамы не было извлечено. Пропускаем.")
                continue

            # Строим полный URL
            full_url = f"https://doramalive.ru{href}"
            print(f"Full URL: {full_url}")

            # Отправляем запрос на страницу дорамы
            drama_response = requests.get(full_url)
            if drama_response.status_code == 200:
                drama_html = drama_response.text
                # Парсинг HTML дорамы
                drama_soup = BeautifulSoup(drama_html, 'html.parser')

                # Извлечение информации
                genres_element = drama_soup.select('div.label-area span.genre')
                genres = [genre.text.strip() for genre in genres_element]
                drama_link_element = drama_soup.select_one('a.btn.btn-danger.start')
                drama_link = f"https://doramalive.ru{drama_link_element['href']}" if drama_link_element and 'href' in drama_link_element.attrs else None

                print(f"Genres: {genres}")
                print(f"Drama Link: {drama_link}")

                # Обновление данных в таблице doramas_info_d
                cursor.execute("UPDATE doramas_info_d SET genres = %s, drama_link = %s WHERE title = %s", (genres, drama_link, title))
                conn.commit()
                print(f"Информация для дорамы '{title}' обновлена.")

            else:
                print(f"Error accessing drama page: {drama_response.status_code}")
                conn.commit()
        # Проверяем наличие ссылки на следующую страницу
        next_page_link = soup.select_one('ul.pager li a.modern-page-next')
        if next_page_link:
            current_page += 1
        else:
            print("Парсинг завершен.")
            break

    else:
        print(f"Error accessing page {current_page_url}: {response.status_code}")
        break

# Закрытие соединения с базой данных
conn.commit()
cursor.close()
conn.close()
