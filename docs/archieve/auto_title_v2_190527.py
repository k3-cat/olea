import re

import requests
from bs4 import BeautifulSoup


class PageCache:
    page_soup = dict()

    @staticmethod
    def clear_cache():
        PageCache.page_soup.clear()


CN_SITE_URL = 'http://scp-wiki-cn.wikidot.com'
EN_SITE_URL = 'http://scp-wiki-cn.wikidot.com'
def get_full_url(url, eng=False):
    BASE_URL = CN_SITE_URL if not eng else EN_SITE_URL


def parse_urls(ino_or_url):
    primary = re.match('^(?:cn-)?([0-9]{3,4})(?:(-j)|(-ex))?$', ino_or_url)
    if primary:
        # SCP-000 SCP-000-J SCP-000-EX
        # SCP-CN-000 SCP-CN-000-J SCP-CN-000-EX
        cache_key, pg = 10, 1
        if '-j' in ino_or_url:
            url = 'joke-scps'
        elif '-ex' in ino_or_url:
            url = 'scp-ex'
            cache_key += 1
        else:
            pg = int(int(primary.group(1)) / 1000) + 1
            url = 'scp-series'
            cache_key += 1 + pg
        if 'cn-' in ino_or_url:
            url = f'{url}-cn'
            cache_key += 10
        if pg != 1:
            url = f'{url}-{pg}'
    elif re.match('^[0-9]{3,4}-jp(-j)?$', ino_or_url):
        url = 'scp-international'
        cache_key = 30
    else:
        url = ino_or_url
        cache_key = 0
    url_ = f'scp-{ino_or_url}' if cache_key != 0 else url
    return url_, url


def fetch_title(info, eng):
    ino_or_url, title = info.split(';')
    if title:
        return title, ino_or_url
    url, index_page_url, cache_key = parse_urls(ino_or_url)
    if cache_key not in PageCache.page_soup:
        html = requests.get(url)
        _soup = BeautifulSoup(html.text, 'lxml')
        PageCache.page_soup[cache_key] = _soup.find_all(
            name='div',
            attrs={'class': 'content-panel standalone series'},
            limit=1)[0]
    main_contant = PageCache.page_soup[cache_key]
    try:
        ele_title = main_contant.find_all(name='a', text=item_text, limit=1)[0]
    except IndexError:
        raise Exception('cannot find title')
    if not ele_title:
        raise Exception('cannot find title')
    return ele_title.parent.text


print(parse_urls('034'))
print(parse_urls('1024'))
print(parse_urls('cn-024'))
print(parse_urls('012-j'))
print(parse_urls('920-EX'))
#print(parse_urls('scp-002-jp'))
print(parse_urls('cn-1024'))
print(parse_urls('cn-048-j'))
print(parse_urls('cn-116-ex'))


# ^(SCP-)?(([0-9]{1,4}-JP)|(CN-[0-9]{1,4})|([0-9]{1,4}))((-J)|(-EX))?$
# all
