from httpcore import TimeoutException
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException

def get_dorama_urls(initial_page_url):
    response = requests.get(initial_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    dorama_links = soup.find_all('div', class_='media-heading')
    return [f"https://doramalive.ru{link.find('a')['href']}" for link in dorama_links]

def navigate_to_next_page(driver):
    try:
        next_page_button = driver.find_element(By.XPATH, '//ul[@class="pager"]//a[contains(text(), "Дальше")]')
        driver.execute_script("arguments[0].click();", next_page_button)
        time.sleep(10)
        return True
    except NoSuchElementException:
        print("Кнопка 'Дальше' не найдена.")
        return False

def get_reviews_from_page(driver, dorama_url):
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

def get_dorama_names(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_list = soup.find('ul', class_='titleList')
    return [li.text for li in title_list.find_all('li')] if title_list else []

def process_dorama(driver, dorama_url):
    dorama_names = get_dorama_names(dorama_url)
    print(f"Названия дорамы: {dorama_names}")

    driver.get(dorama_url)

    try:
        reviews, hidden_reviews = get_reviews_from_page(driver, dorama_url)

        for dorama_name in dorama_names[:1]:  # Используйте только первое имя
            print(f"Дорама: {dorama_name}")
            print("\nОткрытые комментарии:")
            for review in reviews:
                print(review)

            print("\nСкрытые комментарии:")
            for hidden_review in hidden_reviews:
                print(hidden_review)

        # Очистка списков перед обработкой следующей дорамы
        reviews = []
        hidden_reviews = []

    except NoSuchElementException:
        print("Отзывов нет.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Обработка всех страниц с дорамами
current_page = 22

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)

while True:
    try:
        print(f"Обрабатывается страница: {current_page}")

        dorama_urls = get_dorama_urls(f"https://doramalive.ru/dorama/film/?PAGEN_1={current_page}")

        if not dorama_urls:
            print("Нет дорам на странице. Возможно, достигнут конец.")
            break

        for dorama_url in dorama_urls:
            process_dorama(driver, dorama_url)

        current_page += 1

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        break

driver.quit()