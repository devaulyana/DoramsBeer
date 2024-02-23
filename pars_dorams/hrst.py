import requests
from bs4 import BeautifulSoup

def update_dorama_info_list(base_url, start_page):
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

                    print(f"Ссылка на дораму: {dorama_url}")
                    print(f"Название дорамы: {dorama_title}")
                    print(f"Второе название дорамы: {dorama_second_title}")
                    print()
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

update_dorama_info_list(base_url, start_page)
