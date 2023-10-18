from flask import Flask, request, jsonify
import requests
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Налаштування доступу до Google API
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/AleksKozhyn/exchange_rate/exchangerate-401809-b65eee8ee27b.json', scope)
client = gspread.authorize(creds)

# Ключ таблиці Google
SPREADSHEET_KEY = '1WfBDSfW6hj_ILzEp-EILJSOUIfXfTXJTkWKtpxSIPhM'

def update_spreadsheet(request_body):
    # Відкриття Google Таблиці за ключем
    spreadsheet = client.open_by_key(SPREADSHEET_KEY)
    worksheet = spreadsheet.get_worksheet(0)

    # Перетворити дані в формат, який підтримується Google Sheets
    for row in request_body:
        for col in range(len(row)):
            if col == 0:
                try:
                    row[col] = datetime.datetime.strptime(row[col], '%d.%m.%Y').strftime('%Y-%m-%d')
                except ValueError:
                    row[col] = ''

    # Вставити дані в таблицю Google
    worksheet.clear()
    worksheet.update('A1', [["","cc","enname","exchangedate","group","r030","rate","rate_per_unit","txt","units","calcdate"]])
    worksheet.update('A2', request_body)

# Функція для генерації JSON
def generate_request_body(currency_data):
    request_data = []

    for data in currency_data:
        try:
            calcdate = int(data["calcdate"])
        except (ValueError, KeyError):
            calcdate = ""

        request_data.append([
            calcdate,
            data.get("cc", ""),
            data.get("enname", ""),
            data.get("exchangedate", ""),
            int(data.get("group", "")),
            data.get("r030", ""),
            data.get("rate", ""),
            data.get("rate_per_unit", ""),
            data.get("txt", ""),
            data.get("units", "")
        ])

    return request_data

# Маршрут для отримання та оновлення даних
@app.route('/get_currency_data', methods=['GET'])
def get_currency_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Отримуємо курси валют
    currency_url = f"https://bank.gov.ua/NBU_Exchange/exchange_site?start={start_date}&end={end_date}&valcode=usd&sort=exchangedate&order=desc&json"
    response = requests.get(currency_url)
    currency_data = response.json()

    # Генеруємо JSON для оновлення таблиці Google
    request_body = generate_request_body(currency_data)

    # Оновлюємо таблицю Google
    update_spreadsheet(request_body)

    return jsonify({'message': 'Data loaded successfully.'})

if __name__ == '__main__':
    app.run(debug=True)
