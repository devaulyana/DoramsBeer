import openai
import psycopg2
from psycopg2 import OperationalError
import g4f
# openai.api_key ="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"

conn = None 
def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

# Corrected the variable assignment
conn = create_connection(
    "pivo_commeyts", "postgres", "1111", "127.0.0.1", "5432"
)
cursor = conn.cursor()


# # Функция для генерации текста от GPT, оценки пивности и записи в базу данных
# def generate_and_save_beer_comment():
#     prompt = "Генерируйте текст о пиве"
#     response = openai.Completion.create(
#         engine="gpt-4",
#         prompt=prompt,
#         max_tokens=150
#     )
    
#     generated_text = response['choices'][0]['text']

#     # Оценка пивности текста (здесь нужно реализовать свою логику)
#     beer_rating = 0.8

#     # Запись в базу данных
#     cursor.execute("INSERT INTO beer_comments (text, beer_rating) VALUES (%s, %s)", (generated_text, beer_rating))
#     conn.commit()

# # Вызов функции для генерации и записи текста
# generate_and_save_beer_comment()

# # Закрытие соединения с базой данных
# cursor.close()
# conn.close()