import time
from bs4 import BeautifulSoup
import requests
from requests.exceptions import Timeout, ConnectionError

def get_soup(url, wait_time=3, timeout=20):
    try:
        response = requests.get(url, timeout=timeout)
        time.sleep(wait_time)
        return BeautifulSoup(response.text, 'html.parser')

    except Timeout as e:
        raise Timeout(f'タイムアウトしました。 {url}') from e
    except ConnectionError as e:
        raise ConnectionError(f'接続エラーが発生しました。 {url}') from e
    except Exception as e:
        raise Exception(f'その他のエラーが発生しました。 {url}: {str(e)}') from e

def get_page_numbers(base_url, keyword):
    def extract_page_numbers(soup):
        page_na = soup.find(class_='c-pagination__list')
        if not page_na:
            return [], None
        page_num = page_na.find_all(class_='c-pagination__item')
        pages = [int(page.text.strip()) for page in page_num if page.text.strip().isdigit()]
        next_page_link = page_na.find('a', class_='c-pagination__arrow c-pagination__arrow--next')
        next_page_url = next_page_link['href'] if next_page_link else None
        return pages, next_page_url

    url = f"{base_url}{keyword}/"
    pages = []
    while url:
        soup = get_soup(url, wait_time=4)
        if not soup:
            break
        new_pages, url = extract_page_numbers(soup)
        pages.extend(new_pages)
    return pages

def get_urls(base_url, keyword):
    pages = get_page_numbers(base_url, keyword)
    url = base_url + keyword + '/'
    if not pages:
        return [url]
    else:
        return [url + str(page) + '/' for page in pages]

def get_title_links(urls):
    def extract_links(soup):
        contents = soup.find(class_="js-rstlist-info rstlist-info")
        if not contents:
            return []
        return [a.get("href") for a in contents.find_all("a", class_="list-rst__rst-name-target") if a.get("href")]

    title_links = set()
    for url in urls:
        soup = get_soup(url, wait_time=4)
        if not soup:
            continue
        title_links.update(extract_links(soup))
    return list(title_links)

def scrape_shop_info(title_links, alternative_genre):
    shop_info = {
        'shop_name': [],
        'shop_address': [],
        'shop_parent_genre': [],
        'shop_genre': [],
        'shop_url': [],
        'shop_phone': []
    }

    for title_link in title_links:
        soup = get_soup(title_link, wait_time=4)
        if not soup:
            continue
        shop_info['shop_name'].append(
            soup.find(class_="rstinfo-table__name-wrap").text.strip() if soup.find(class_="rstinfo-table__name-wrap") else ""
        )
        shop_address_tag = soup.find("p", class_="rstinfo-table__address")
        shop_info['shop_address'].append(
            shop_address_tag.text.strip() if shop_address_tag else ""
        )
        shop_info['shop_parent_genre'].append(alternative_genre)
        shop_genre_tag = soup.select_one("#rst-data-head > table:nth-child(2) > tbody > tr:nth-child(2) > td > span")
        shop_info['shop_genre'].append(
            shop_genre_tag.text.strip() if shop_genre_tag else alternative_genre
        )
        shop_url_tag = soup.find(class_="homepage")
        shop_info['shop_url'].append(
            shop_url_tag.find("a")["href"] if shop_url_tag else ""
        )
        shop_phone_tag = soup.find(class_="rstinfo-table__tel-num")
        shop_info['shop_phone'].append(
            shop_phone_tag.text.strip() if shop_phone_tag else ""
        )
    return shop_info

