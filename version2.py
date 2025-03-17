import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://hh.ru/search/vacancy'
SEARCH_QUERY = 'python'
ITEMS_PER_PAGE = 100
AREA_ID = 1
HEADERS = {
    'Host': 'hh.ru',
    'User-Agent': 'Safari',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

def get_url(query, items_per_page, area_id, page=0):
    params = {
        'text': query,
        'items_on_page': items_per_page,
        'area': area_id,
        'page': page
    }
    return f"{BASE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

def fetch_html(url):
    response = requests.get(url, headers=HEADERS)
    return response.text

def parse_paginator(html):
    soup = BeautifulSoup(html, 'html.parser')
    paginator = soup.find_all("span", {'class': 'pager-item-not-in-short-range'})
    page_numbers = [int(page.find('a').text) for page in paginator]
    return page_numbers[-1] if page_numbers else 1

def parse_job(job_element):
    title_tag = job_element.find('a')
    company_tag = job_element.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).find('a')
    title = title_tag.text.strip() if title_tag else 'Название не указано'
    company = company_tag.text.strip() if company_tag else 'Компания не указана'
    return {'title': title, 'company': company}

def extract_jobs(html):
    soup = BeautifulSoup(html, 'html.parser')
    job_elements = soup.find_all('div', {'class': 'vacancy-serp-item'})
    return [parse_job(job) for job in job_elements]

def get_max_page():
    url = get_url(SEARCH_QUERY, ITEMS_PER_PAGE, AREA_ID)
    html = fetch_html(url)
    return parse_paginator(html)

def get_jobs(last_page):
    all_jobs = []
    for page in range(last_page):
        url = get_url(SEARCH_QUERY, ITEMS_PER_PAGE, AREA_ID, page)
        html = fetch_html(url)
        all_jobs.extend(extract_jobs(html))
    return all_jobs

if __name__ == "__main__":
    max_page = get_max_page()
    jobs = get_jobs(max_page)
    for job in jobs:
        print(job)