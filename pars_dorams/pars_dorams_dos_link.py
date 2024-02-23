import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.errors import OperationalError

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


def update_dorama_info_list(conn, cursor, base_url, start_page):
    current_page = start_page

    while True:
        current_page_url = f"{base_url}/page/{current_page}"

        response = requests.get(current_page_url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            doramas = soup.select('div.img-link a')
            for dorama in doramas:
                dorama_url = dorama['href']
                dorama_title_element = dorama.find('span')
                dorama_title = dorama_title_element.text.strip() if dorama_title_element else None

                # Извлечение вторых названий дорамы
                response_dorama = requests.get(dorama_url)
                if response_dorama.status_code == 200:
                    soup_dorama = BeautifulSoup(response_dorama.text, 'html.parser')
                    second_title_em = dorama.find_next('em')
                    dorama_second_title = second_title_em.text.strip() if second_title_em else None

                    # Обновление данных в базе данных
                    cursor.execute("UPDATE doramas_info_d SET drama_link_club = %s WHERE %s = ANY (other_titles)",
                                   (dorama_url, dorama_second_title))
                    conn.commit()
                    print(f"Ссылка на дораму добавлена в базу данных: {dorama_url}")
                else:
                    print(f"Error accessing dorama page {dorama_url}: {response_dorama.status_code}")

            next_page_link = soup.select_one('a.next.page-numbers')
            if next_page_link:
                current_page += 1
            else:
                break
        else:
            print(f"Error accessing page {current_page_url}: {response.status_code}")
            break

# Пример использования
base_url = "https://mydoramy.club/filmy"
start_page = 1

update_dorama_info_list(conn, cursor, base_url, start_page)

# Закрытие соединения с базой данных
conn.commit()
cursor.close()
conn.close()