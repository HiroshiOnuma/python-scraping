import pandas as pd
import requests
from def_scraping import get_urls, get_title_links, scrape_shop_info

from dotenv import load_dotenv
load_dotenv()
import os

base_url = os.getenv('BASE_URL')
keyword = os.getenv('KEYWORD')
alternative_genre = os.getenv('ALTERNATIVE_GENRE')
file_name = os.getenv('FILE_NAME')

try:
    urls = get_urls(base_url, keyword)
    print(urls)

    title_links = get_title_links(urls)
    print(title_links)
    print(len(title_links))

    shop_info = scrape_shop_info(title_links, alternative_genre)
    print(shop_info)
    
except requests.Timeout as e:
    print(e)
except requests.ConnectionError as e:
    print(e)
except Exception as e:
    print(e)

# 結果をDataFrameに変換
df = pd.DataFrame(shop_info)
print(df)

# DataFrameをCSVファイルに保存
df.to_csv(f'csv_files/{file_name}', index=False, encoding='utf-8')