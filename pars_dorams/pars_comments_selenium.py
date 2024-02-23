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


def get_dorama_name(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_list = soup.find('ul', class_='titleList')
    return [li.text for li in title_list.find_all('li')] if title_list else []


def navigate_to_next_page(driver, next_page_url):
    try:
        next_page_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, f'//ul[@class="pager"]//a[contains(text(), "Дальше")]'))
        )

        driver.execute_script("arguments[0].click();", next_page_button)
        
        WebDriverWait(driver, 30).until(
            EC.url_changes(driver.current_url)
        )
    except Exception as e:
        print(f"Произошла ошибка при переходе на следующую страницу: {e}")

def get_comments_from_page(driver):
    comments = []

    reviews_tab = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-type="review"]'))
    )
    reviews_tab.click()
    time.sleep(10) 

    current_page = 1
    while True:
        try:
            reviews_page_source = driver.page_source

            soup = BeautifulSoup(reviews_page_source, 'html.parser')

            comment_blocks = soup.find_all('div', class_='item')

            for comment_block in comment_blocks:
                comment_div = comment_block.find('div', class_='detail-more')
                if comment_div:
                    comment_text = comment_div.find('p').text
                    comments.append(comment_text)

            next_page_button = driver.find_element(By.XPATH, '//ul[@class="pager"]//a[contains(text(), "Дальше")]')

            driver.execute_script("arguments[0].click();", next_page_button)
            time.sleep(30)  
            current_page += 1

        except NoSuchElementException:
            print("Кнопка 'Дальше' не найдена. Завершение цикла.")
            break

    return comments


initial_page_url = "https://doramalive.ru/dorama/film/"
dorama_urls = get_dorama_urls(initial_page_url)


for dorama_url in dorama_urls:
    print(f"Обрабатывается дорама: {dorama_url}")

    dorama_names = get_dorama_name(dorama_url)
    print(f"Названия дорамы: {dorama_names}")

    comments = []

    driver = webdriver.Chrome()
    driver.get(dorama_url)

    try:
        comments.extend(get_comments_from_page(driver))
    finally:
        driver.quit()

    print(f"Комментарии: {comments}")
