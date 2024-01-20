import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from google.oauth2 import service_account
import gspread

# Параметри підключення до PostgreSQL
postgres_hostname = "hostname"
postgres_port = port
postgres_dbname = "db_name"
postgres_user = "username"
postgres_password = "password"

engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}@{postgres_hostname}/{postgres_dbname}')

google_sheets_key_path = "path to Google API key json"

credentials = service_account.Credentials.from_service_account_file(google_sheets_key_path, scopes=['https://spreadsheets.google.com/feeds'])
gc = gspread.authorize(credentials)

google_sheets_url = "Google Sheets URL"

spreadsheet = gc.open_by_url(google_sheets_url)
sheets = spreadsheet.worksheets()


for sheet in sheets:
    df = pd.DataFrame(sheet.get_all_records())
    postgres_table_name = sheet.title
    df.to_sql(postgres_table_name, engine, if_exists='replace', index=False)
