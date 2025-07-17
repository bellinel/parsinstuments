from multiprocessing import Process

from get_table import get_table, upload_to_google_sheets_by_url


#

def run_etm():
    import etm
    etm.parse_etm()

def run_vseinstr():
    import vseinstr
    vseinstr.parse_vseinstrumenti()

if __name__ == "__main__":
    print("🚀 Загрузка таблицы...")
    get_table()
    
    print("🚀 Запуск парсеров в отдельных процессах...")
    p1 = Process(target=run_vseinstr)
    p2 = Process(target=run_etm)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("✅ Парсинг завершён")
    
    upload_to_google_sheets_by_url()