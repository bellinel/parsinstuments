
import os
import gspread
from google.oauth2.service_account import Credentials
import json



def get_table():
    creds = Credentials.from_service_account_file(
    "creds.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

    gc = gspread.authorize(creds)

    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Xmu5d2BLW8C4PVYV31xaRAaQTnx0eX6ZCMMeANuYzRU")

    worksheet = spreadsheet.worksheet("Без скрытых полей")

    row_count = worksheet.row_count
    data = worksheet.get(f'A1:G{row_count}')

    # Первая строка — заголовки
    headers = data[0]
    rows = data[1:]


    json_list = []
    for row in rows:
        
        # Заполняем недостающие поля значением "не найден артикул на сайте"
        while len(row) < 5:
            row.append("не найден артикул на сайте")
            
        if 'CКИНЗ' in row[1]:
            print(row[1])
            continue
        if 'Cкинз' in row[1]:
            print(row[1])
            continue

        if 'Cкинз' in row[1]:
            print(row[1])
            continue

        if 'СКИНЗ' in row[1]:
            print(row[1])
            continue
        
        item = {
            'артикул': row[0] if row[0] else "не найден артикул на сайте",
            'наименование товара': row[1] if row[1] else "не найден артикул на сайте",
            'прайс': row[2] if row[2] else "не найден артикул на сайте",
            
        }   
        json_list.append(item)

    # Запишем в файл
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(json_list, f, ensure_ascii=False, indent=4)

    print("Данные успешно записаны в output.json")


def load_items_from_json():
    with open('output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items_list = []
    for item in data:
        # Создаём словарь с нужными ключами
        record = {
            'артикул': item.get('артикул'),
            'название': item.get('наименование товара'),
            'цена': item.get('прайс')
        }
        items_list.append(record)

    return items_list

def load_items_from_json_for_etm():
    file_path = 'output.json'

    if not os.path.exists(file_path):
        raise FileNotFoundError("Файл 'output.json' не найден.")

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка в структуре JSON: {e}")

    if not isinstance(data, list):
        raise TypeError("Ожидался список объектов в JSON.")

    items_list = []
    for item in data:
        
        
        record = {
            'артикул': item.get('артикул'),
            'бренд': item.get('бренд'),
            'название': item.get('название'),
            'цена etm': item.get('цена etm')
        }
        
        items_list.append(record)

    return items_list
    


import gspread
import json
from google.oauth2.service_account import Credentials

def upload_to_google_sheets_by_url():
    import gspread
    import json
    from google.oauth2.service_account import Credentials

    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Xmu5d2BLW8C4PVYV31xaRAaQTnx0eX6ZCMMeANuYzRU"
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("creds.json", scopes=scopes)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(spreadsheet_url)

    # Создаем или очищаем Лист3
    try:
        new_sheet = spreadsheet.add_worksheet(title="Лист3", rows="4000", cols="10")
    except gspread.exceptions.APIError:
        new_sheet = spreadsheet.worksheet("Лист3")
        new_sheet.clear()

    # Загружаем JSON-файлы
    with open('all_data_vseinstrumenti.json', 'r', encoding='utf-8') as f1:
        vseinstr_data = json.load(f1)
    with open('all_data_etm.json', 'r', encoding='utf-8') as f2:
        etm_data = json.load(f2)

    # Объединяем данные по артикулу
    vseinstr_map = {item['артикул']: item for item in vseinstr_data}
    etm_map = {item['артикул']: item for item in etm_data}
    all_articles = list(set(vseinstr_map.keys()) | set(etm_map.keys()))

    merged_data = []

    for art in all_articles:
        v_item = vseinstr_map.get(art, {})
        e_item = etm_map.get(art, {})

        brand = v_item.get('бренд') or e_item.get('бренд') or 'не найден артикул на сайте'
        name = v_item.get('название') or e_item.get('название') or 'не найден артикул на сайте'
        vse_price = v_item.get('цена vseinstrumenti') or 'не найден артикул на сайте'
        vse_change = v_item.get('изменение (%)', 'не найден артикул на сайте')
        etm_price = e_item.get('цена etm') or e_item.get('цена') or 'не найден артикул на сайте'
        etm_change = e_item.get('изменение (%)', 'не найден артикул на сайте')

        row = [art, brand, name, vse_price, vse_change, etm_price, etm_change]
        merged_data.append(row)

    # Сортируем по названию (3-й элемент строки, индекс 2)
    merged_data.sort(key=lambda x: str(x[2]).lower())

    # Заголовки
    headers = ['Артикул', 'Бренд', 'Название', 'Цена Vseinstrumenti', '% изм. Vseinstr', 'Цена ETM', '% изм. ETM']
    data = [headers] + merged_data

    # Загрузка данных
    new_sheet.clear()
    new_sheet.update(data)

    print("✅ Данные успешно загружены в Лист3 таблицы (отсортировано по названию)!")

