import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC    
from get_table import load_items_from_json
from vseinstr import parse_price
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def parse_etm():
    names = load_items_from_json()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    all_data = []

    for name in names:
        query = name.get('артикул')
        if not query:
            continue

        current_brand = None

        url = f'https://www.etm.ru/catalog?searchValue={query}'
        driver.get(url)
        wait = WebDriverWait(driver, 3)

        try:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tss-o60ib4-grid_item')))
                products = driver.find_elements(By.CSS_SELECTOR, 'div.tss-o60ib4-grid_item')
                for product in products:
                    brand = product.find_element(By.CSS_SELECTOR, 'div.tss-izaetf-good_descr a').text.strip()
                    if brand in ['SITOMO', 'HORTZ']:
                        current_brand = brand
                        break
                if not current_brand:
                    raise ValueError("Не найден нужный бренд")
            except:
                # Переход к поиску по названию
                query = name.get('название')
                driver.get(f'https://www.etm.ru/catalog?searchValue={query}')
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tss-o60ib4-grid_item')))
                products = driver.find_elements(By.CSS_SELECTOR, 'div.tss-o60ib4-grid_item')
                for product in products:
                    brand = product.find_element(By.CSS_SELECTOR, 'div.tss-izaetf-good_descr a').text.strip()
                    if brand in ['SITOMO', 'HORTZ']:
                        current_brand = brand
                        break
                if not current_brand:
                    raise ValueError("Не найден нужный бренд")
            

            price_elem = product.find_element(By.CSS_SELECTOR, 'p.tss-1mz6fdu-priceColor-priceCount')
            new_price_str = price_elem.text

            old_price_str = name.get('цена')
            old_price = parse_price(old_price_str)
            new_price = parse_price(new_price_str)

            data = {
                'артикул': name.get('артикул'),
                'бренд': current_brand,
                'название': name.get('название'),
                'цена etm': new_price,
                'изменение (%)': None
            }

            if isinstance(old_price, (int, float)) and isinstance(new_price, (int, float)):
                try:
                    percent_change = ((new_price - old_price) / old_price) * 100
                    data['изменение (%)'] = round(percent_change, 2)
                except ZeroDivisionError:
                    data['изменение (%)'] = 0
            else:
                data['изменение (%)'] = 'не найден артикул на сайте'

            print(f'ETM: {data}')
            all_data.append(data)

        except Exception as e:
            print(f"Ошибка при поиске товара {query}: {e}")
            data = {
                'артикул': name.get('артикул'),
                'бренд': current_brand or 'не найден',
                'название': name.get('название'),
                'цена etm': 'не найден артикул',
                'изменение (%)': 'не найден артикул'
            }
            print(e)
            all_data.append(data)

    with open('all_data_etm.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    driver.quit()


def main():
    parse_etm()


if __name__ == '__main__':
    main()
