import requests
import threading
from bs4 import BeautifulSoup

def get_http(path):
    try:
        return requests.get(path)
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException,
            requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(str(e))
        return False
    
def save_search(all_pages, search, content_type):
    search = search.replace('%20', ' ')[3:]

    f = open('{} {}.txt'.format(search, content_type), 'w', encoding='utf-8')
    f.write('Results found for \'{}\':'.format(search))
    for i in range((int(len(all_pages)))):
        for j in range((int(len(all_pages[i])))):
            f.write('\n\n' + str(all_pages[i][j]))
    f.close()

def search_content(search, n_pages, content_type):

    def scrap_content(url, path, n_page, content_type):
        nonlocal all_pages

        if content_type == 'books':
            div_class = 'resItemBox resItemBoxBooks exactMatch'
        else:
            div_class = 'resItemBox resItemBoxArticles exactMatch'
        
        r = get_http(url + path)
        if r == False:
                return
                
        # print('Searching content on page {}...'.format(n_page))
        soup = BeautifulSoup(r.text, 'lxml')
        contents = soup.find_all('div', {'class': div_class})

        content_list = []
        content_list.append('----------------------------------- Page {} -----------------------------------'.format(n_page))
        for content in contents:
            # Title
            content_info = (content.find('h3', {'itemprop': 'name'})).a.string
            # Authors
            content_info += '\n('
            authors = [author for author in content.find_all('a', {'itemprop': 'author'})]
            for i in range(len(authors)):
                content_info += '{}'.format(authors[i].string)
                if (i + 1) < len(authors):
                    content_info += ', '
            content_info += ')'
            #Year
            try:
                year = content.find('div', {'class': 'bookProperty property_year'}).find('div', {'class': 'property_value'}).string
            except AttributeError:
                year = 'Not informed'
            finally:
                content_info += '\nYear: {}'.format(year)
            # Language
            try:
                language = content.find('div', {'class': 'bookProperty property_language'}).find('div', {'class': 'property_value'}).string
            except AttributeError:
                language = 'Not informed'
            finally:
                content_info += ' | Language: {}'.format(language)
            # File
            content_info += ' | File: {}'.format((content.find('div', {'class': 'bookProperty property__file'})).find('div', {'class': 'property_value'}).string)
            # Access
            content_info += '\nAccess: {}'.format(url + content.a.get('href'))
            
            content_list.append(content_info)
            # print('\n' + content_info)

        all_pages.append(content_list)

    if content_type == 'books':
        url = 'https://b-ok.lat'
    else:
        url = 'https://booksc.org'

    all_pages = []
    all_threads = []
    path = search
    for n_page in range(1, n_pages + 1):
        t = threading.Thread(target=scrap_content, args=(url, path, n_page, content_type))
        t.start()
        all_threads.append(t)
        path = search + '?page=' + str(n_page + 1)
        if (n_page + 1) == 10:
            break

    for t in all_threads:
        t.join()
    
    all_pages.sort()
    for n_page in range(10, n_pages + 1):
        t = threading.Thread(target=scrap_content, args=(url, path, n_page, content_type))
        t.start()
        t.join()
    
    save_search(all_pages, search, content_type)

def crawler_start(content='1', search='', n_pages=1):
    book_content = ['1', 'BOOK', 'BOOKS', '3', 'BOTH']
    article_content = ['2', 'ARTICLE', 'ARTICLES', '3', 'BOTH']
    content = content.upper()

    search = '/s/' + search.replace(' ', '%20')
    if n_pages > 10:
        n_pages = 10
    
    all_threads = []
    if content in book_content:
        t = threading.Thread(target=search_content, args=(search, n_pages, 'books'))
        t.start()
        all_threads.append(t)
    if content in article_content:
        t = threading.Thread(target=search_content, args=(search, n_pages, 'articles'))
        t.start()
        all_threads.append(t)

    for t in all_threads:
        t.join()

if __name__ == '__main__':
    all_content = ['1', 'BOOK', 'BOOKS', '2', 'ARTICLE', 'ARTICLES', '3', 'BOTH']
    content = ''
    print('------------------------- Z-Library Crawler -------------------------')
    print('Content types:\n1. Books\n2. Articles\n3. Both\n')
    while content not in all_content:
        content = input('Content type: ')
    search = input('Keywords: ')
    n_pages = int(input('Number of search pages (max 10): '))
    
    print('Crawler started...')
    crawler_start(content, search, n_pages)
    print('Crawler finished.')