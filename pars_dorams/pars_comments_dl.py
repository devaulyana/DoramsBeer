import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException
import psycopg2
from psycopg2.errors import OperationalError
from httpcore import TimeoutException


# Подключение к базе данных
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


# Получение id из базы данных
def get_dorama_id_by_name(cursor, dorama_names):
    try:
        cursor.execute("BEGIN;")
        cursor.execute("SELECT dorama_id FROM dorama_reviews_open WHERE %s = ANY(other_titles);", ([dorama_names]))
        result = cursor.fetchone()
        cursor.execute("COMMIT;")
        return result[0] if result else None
    except psycopg2.Error as e:
        cursor.execute("ROLLBACK;")
        print(f"Произошла ошибка при получении ID дорамы: {e}")
        return None


# def update_comments(cursor, dorama_id, comments, hidden_comments, conn):
#     try:
#         # Split comments into list.
#         comments_list = comments.split('\n')
#         hidden_comments_list = hidden_comments.split('\n')

#         # Make hidden_comments_list the same length as comments_list.
#         hidden_comments_list += [''] * (len(comments_list) - len(hidden_comments_list))

#         for comment, hidden_comment in zip(comments_list, hidden_comments_list):
#             # Just skip all the empty comments.
#             if comment.strip() == '' and hidden_comment.strip() == '':
#                 continue

#             # Add visible comments.
#             if comment.strip() != '':
#                 insert_query = "INSERT INTO dorama_reviews_open (dorama_id, open_comments_text_dl) VALUES (%s, %s);"
#                 cursor.execute(insert_query, (dorama_id, comment.strip()))

#             # Add hidden comments.
#             if hidden_comment.strip() != '':
#                 insert_query = "INSERT INTO dorama_reviews_hidden (dorama_id, hidden_comment_text_dl) VALUES (%s, %s);"
#                 cursor.execute(insert_query, (dorama_id, hidden_comment.strip()))

#         conn.commit()
#         print(f"Отзывы для дорамы с ID {dorama_id} успешно обновлены.")
#     except psycopg2.Error as e:
#         print(f"Произошла ошибка при обновлении отзывов: {e}")


def get_dorama_urls(initial_page_url):
    response = requests.get(initial_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    dorama_links = soup.find_all('div', class_='media-heading')
    return [f"https://doramalive.ru{link.find('a')['href']}" for link in dorama_links]


def get_dorama_name(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_list = soup.find('ul', class_='titleList')
    return [li.text for li in title_list.find_all('li')] if title_list else []


def navigate_to_next_page(driver):
    try:
        next_page_button = driver.find_element(By.XPATH, '//ul[@class="pager"]//a[contains(text(), "Дальше")]')
        driver.execute_script("arguments[0].click();", next_page_button)
        time.sleep(10)
        return True
    except NoSuchElementException:
        print("Кнопка 'Дальше' не найдена.")
        return False


def get_reviews_from_page(driver):
    reviews = []
    hidden_reviews = []

    try:
        reviews_tab = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-type="review"]'))
        )
        reviews_tab.click()
        time.sleep(10)
    except TimeoutException:
        print("Отзывов нет или кнопка 'Отзывы' не найдена. Пропуск дорамы.")
        return reviews, hidden_reviews

    while True:
        try:
            reviews_page_source = driver.page_source
            soup = BeautifulSoup(reviews_page_source, 'html.parser')

            review_blocks = soup.find_all('div', class_='item')

            for review_block in review_blocks:
                review_div = review_block.find('div', class_='fulltext detail-more')
                if review_div:
                    review_text_elem = review_div.find('p')
                    reviews.append(review_text_elem.text if review_text_elem else "")

                # Проверка для скрытых отзывов
                hidden_review_div = review_block.find('div', class_='detail-more', style='display: none;')
                if hidden_review_div:
                    hidden_review_text_elem = hidden_review_div.find('p')
                    hidden_reviews.append(hidden_review_text_elem.text if hidden_review_text_elem else "")

            if not navigate_to_next_page(driver):
                break
        except Exception as e:
            print(f"Произошла ошибка при загрузке страницы: {str(e)}")
            break

    return reviews, hidden_reviews


def process_dorama(driver, conn, cursor, dorama_url):
    dorama_names = get_dorama_name(dorama_url)
    print(f"Названия дорамы: {dorama_names}")

    driver.get(dorama_url)

    try:
        reviews, hidden_reviews = get_reviews_from_page(driver)

        for dorama_name in dorama_names:
            dorama_id = get_dorama_id_by_name(cursor, dorama_name)

            if dorama_id is not None:
                # Добавляем открытые отзывы
                for review in reviews:
                    if review.strip():
                        insert_query = "INSERT INTO dorama_reviews_open (dorama_id, open_comments_text_dl) VALUES (%s, %s);"
                        cursor.execute(insert_query, (dorama_id, review.strip()))

                # Добавляем скрытые отзывы
                for hidden_review in hidden_reviews:
                    if hidden_review.strip():
                        insert_query = "INSERT INTO dorama_reviews_hidden (dorama_id, hidden_comment_text_dl) VALUES (%s, %s);"
                        cursor.execute(insert_query, (dorama_id, hidden_review.strip()))

                # Коммит для каждой дорамы
                conn.commit()

                # Очистка списков перед обработкой следующей дорамы
                reviews = []
                hidden_reviews = []
                print(f"Отзывы для дорамы с ID {dorama_id} успешно обновлены.")
            else:
                print(f"ID для дорамы '{dorama_name}' не найден. Пропуск обработки.")


        # Очистка списков перед обработкой следующей дорамы
        reviews = []
        hidden_reviews = []

    except NoSuchElementException:
        print("Отзывов нет.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)

conn = create_connection(
    "pivo_commets", "postgres", "1111", "127.0.0.1", "5432"
)
cursor = conn.cursor()

# Обработка всех страниц с дорамами


for current_page in range(89,90):  # Установите максимальное значение страницы вместо 100
    try:
        print(f"Обрабатывается страница: {current_page}")

        dorama_urls = get_dorama_urls(f"https://doramalive.ru/dorama/film/?PAGEN_1={current_page}")

        if not dorama_urls:
            print("Нет дорам на странице. Возможно, достигнут конец.")
            break

        for dorama_url in dorama_urls:
            process_dorama(driver, conn, cursor, dorama_url)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        break

driver.quit()

cursor.close()
conn.close()
