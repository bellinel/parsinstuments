import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC    
import time
import re
import asyncio
from get_table import load_items_from_json  # предполагаем, что это синхронная функция
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def parse_price(price_str):
    # Убираем всё, кроме цифр и точки/запятой
    p_clean = re.sub(r'[^\d.,]', '', price_str)
    p_clean = p_clean.replace(',', '.')
    try:
        return float(p_clean)
    except:
        return None

def parse_vseinstrumenti():
    names = load_items_from_json()
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    all_data = []
   
    for name in names:
        query = name.get('артикул')
        
        if not query:
            continue

        url = f'https://www.vseinstrumenti.ru/search?what={query}'
        driver.get(url)

        wait = WebDriverWait(driver, 3)
        target_product = None

        try:
            try:
                product = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-qa="products-tile"]')))
                products = driver.find_elements(By.CSS_SELECTOR, 'div[data-qa="products-tile"]')
                
                for product in products:
                    brand_text = product.find_element(By.CSS_SELECTOR, 'a[data-qa="product-name"] span').text.lower()
                    
                    
                    if any(brand in brand_text for brand in ['hortz']):
                        target_product = product
                        
                        break
                    elif any(brand in brand_text for brand in ['sitomo']):
                        target_product = product
                        
                        break
                        
                
                if not target_product:
                    raise Exception("Не найден нужный бренд")
                
            except:
                query = name.get('название')
                
                driver.get(f'https://www.vseinstrumenti.ru/search?what={query}')
                product = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-qa="products-tile"]')))
                products = driver.find_elements(By.CSS_SELECTOR, 'div[data-qa="products-tile"]')
                target_product = None
                for product in products:
                    brand_text = product.find_element(By.CSS_SELECTOR, 'a[data-qa="product-name"] span').text.lower()
                    
                    
                    if any(brand in brand_text for brand in ['hortz']):
                        target_product = product
                        
                        break
                    elif any(brand in brand_text for brand in ['sitomo']):
                        target_product = product
                        
                        break
                
                
                if not target_product:
                    raise Exception("Не найден нужный бренд")    
                
            
            price_elem = product.find_element(By.CSS_SELECTOR, 'p[data-qa="product-price-current"]')  # локальный поиск относительно product
            new_price_str = price_elem.text
            

            old_price_str = name.get('цена')

            old_price = parse_price(old_price_str)
            new_price = parse_price(new_price_str)
            
           
           

           

            data = {
                'артикул': name.get('артикул'),
                'цена vseinstrumenti': new_price,
                'изменение (%)': None
                
            }

            if old_price == 'не найден артикул на сайте':
                data['изменение (%)'] = 'не найден артикул на сайте'
                all_data.append(data)
                
                continue

            if old_price and new_price:
                try:
                    
                        percent_change = ((new_price - old_price) / old_price) * 100
                        percent_change = round(percent_change, 2)
                        data['изменение (%)'] = percent_change
                        # if abs(percent_change) > 5:
                        #     data['изменение (%)'] = percent_change
                except ZeroDivisionError:
                        data['изменение (%)'] = 0
            all_data.append(data)
            print(f'VSEINSTR: {brand_text,data}')
            
        except Exception as e:
            print(f"Ошибка при поиске товара {query}")
            data = {
                'артикул': name.get('артикул'),
                'цена vseinstrumenti': 'не найден артикул на сайте',
                'изменение (%)': 'не найден артикул на сайте'   
            }
            print(f'VSEINSTR: {data}')
            all_data.append(data)

    with open('all_data_vseinstrumenti.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

        #     if old_price is not None and new_price is not None:
        #         change = abs(new_price - old_price) / old_price
        #         if change >= 0.05:
        #             name['цена_изменилась'] = True
        #             name['процент_изменения'] = round(change * 100, 2)
        #         else:
        #             name['цена_изменилась'] = False
        #     else:
        #         print(f"Не удалось распарсить цены для {query}: old_price={old_price_str}, new_price={new_price_str}")




       

    driver.quit()

def main():
    parse_vseinstrumenti()


if __name__ == '__main__':
    main()
