
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

    worksheet = spreadsheet.worksheet("Данные для парсинга")

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

    try:
        sheet = spreadsheet.add_worksheet(title="Спаршенные данные", rows="4000", cols="10")
    except gspread.exceptions.APIError:
        sheet = spreadsheet.worksheet("Спаршенные данные")
        sheet.clear()

    # Загружаем данные
    with open('output.json', 'r', encoding='utf-8') as f_base:
        base_data = json.load(f_base)
    with open('all_data_vseinstrumenti.json', 'r', encoding='utf-8') as f1:
        vseinstr_data = json.load(f1)
    with open('all_data_etm.json', 'r', encoding='utf-8') as f2:
        etm_data = json.load(f2)

    vseinstr_map = {item['артикул']: item for item in vseinstr_data if 'артикул' in item}
    etm_map = {item['артикул']: item for item in etm_data if 'артикул' in item}

    rows = []
    highlight_cells = []  # [(col_letter, row_number)]
    clear_cells = []
    for idx, base_item in enumerate(base_data):
        art = base_item.get('артикул', '')
        name = base_item.get('наименование товара', '')
        price = base_item.get('прайс', '')
        vse_price = ''
        vse_change = ''
        etm_price = ''
        etm_change = ''
        if art in vseinstr_map:
            vse_price = vseinstr_map[art].get('цена vseinstrumenti', '')
            vse_change = vseinstr_map[art].get('изменение (%)', '')
        if art in etm_map:
            etm_price = etm_map[art].get('цена etm', '')
            etm_change = etm_map[art].get('изменение (%)', '')
        rows.append([art, name, price, vse_price, vse_change, etm_price, etm_change])

        row_num = idx + 2  # +2, т.к. первая строка — заголовки
        # Проверяем % изм. Vseinstr (E)
        try:
            vse_pct = float(str(vse_change).replace('%','').replace(',','.'))
            if vse_pct != 0:
                highlight_cells.append(('E', row_num))
            else:
                clear_cells.append(('E', row_num))
        except:
            clear_cells.append(('E', row_num))
        # Проверяем % изм. ETM (G)
        try:
            etm_pct = float(str(etm_change).replace('%','').replace(',','.'))
            if etm_pct != 0:
                highlight_cells.append(('G', row_num))
            else:
                clear_cells.append(('G', row_num))
        except:
            clear_cells.append(('G', row_num))

    headers = ['Артикул', 'Наименование', 'Прайс', 'Цена Vseinstrumenti', '% изм. Vseinstr', 'Цена ETM', '% изм. ETM']
    data = [headers] + rows

    sheet.clear()
    sheet.update(values=data)

    # Формируем batch_update запросы
    requests = []
    # Подсветка жёлтым
    for col, row in highlight_cells:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": row-1,
                    "endRowIndex": row,
                    "startColumnIndex": ord(col)-ord('A'),
                    "endColumnIndex": ord(col)-ord('A')+1
                },
                "cell": {"userEnteredFormat": {"backgroundColor": {"red":1, "green":1, "blue":0}}},
                "fields": "userEnteredFormat.backgroundColor"
            }
        })
    # Очистка цвета
    for col, row in clear_cells:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": row-1,
                    "endRowIndex": row,
                    "startColumnIndex": ord(col)-ord('A'),
                    "endColumnIndex": ord(col)-ord('A')+1
                },
                "cell": {"userEnteredFormat": {"backgroundColor": {"red":1, "green":1, "blue":1}}},
                "fields": "userEnteredFormat.backgroundColor"
            }
        })
    if requests:
        sheet.spreadsheet.batch_update({"requests": requests})

    print("✅ Данные записаны, подсветка применена пакетно!")





