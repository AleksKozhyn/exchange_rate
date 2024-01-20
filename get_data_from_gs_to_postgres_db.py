import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from google.oauth2 import service_account
import gspread

# Параметри підключення до PostgreSQL
postgres_hostname = "localhost"
postgres_port = 5432
postgres_dbname = "test_task"
postgres_user = "ask"
postgres_password = "123456"

# Підключення до PostgreSQL
engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}@{postgres_hostname}/{postgres_dbname}')

# Шлях до ключа API Google (JSON-файл)
google_sheets_key_path = "/home/ask/TestTask/exchangerate-401809-18c59b07649c.json"

# Створення об'єкта для доступу до Google Таблиць
credentials = service_account.Credentials.from_service_account_file(google_sheets_key_path, scopes=['https://spreadsheets.google.com/feeds'])
gc = gspread.authorize(credentials)

# Посилання на таблицю
google_sheets_url = "https://docs.google.com/spreadsheets/d/1udzgLJ2UxFGFMVBglwJlHsaVYC_fJLnB-DtP54WtVOs/edit#gid=0"

# Відкриваємо таблицю
spreadsheet = gc.open_by_url(google_sheets_url)

# Отримуємо список листів
sheets = spreadsheet.worksheets()

# Цикл для обробки кожного листа
for sheet in sheets:
    # Отримуємо дані з листа
    df = pd.DataFrame(sheet.get_all_records())

    # Задаємо ім'я таблиці у PostgreSQL використовуючи назву листа
    postgres_table_name = sheet.title

    # Завантаження даних у PostgreSQL
    df.to_sql(postgres_table_name, engine, if_exists='replace', index=False)
