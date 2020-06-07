import re

import requests
from bs4 import BeautifulSoup
from flask import current_app

from models import ProjType
from olea.errors import InvalidSource
from olea.exts import redis

CN_SITE_URL = 'http://scp-wiki-cn.wikidot.com'
WEB_EXP = current_app.config['WEB_EXP']


def fetch_web(url):
    web_page_t = redis.get(url)
    if not web_page_t:
        web_page = requests.get(f'{CN_SITE_URL}/{url}')
        if web_page.status_code == 404:
            raise InvalidSource(rsn=InvalidSource.Rsn.web, url=url)
        web_page_t = web_page.text
    redis.set(url, web_page_t, ex=WEB_EXP)
    soup = BeautifulSoup(web_page_t, 'lxml')
    return soup.find('div', {'id': 'main-content'})


def fetch_title_by_url(url):
    if not re.match(r'^/[a-z]+(?:(?:-[a-z]+)+)?$', url):
        raise InvalidSource(rsn=InvalidSource.Rsn.inp)

    web = fetch_web(url)
    title_e = web.find('div', {'id': 'page-title'})
    return title_e.text.strip()


def fetch_title_by_id(id_):
    if primary := re.match(r'^(?:cn-)?([0-9]{3,4})(?:(?:-j)|(?:-ex))?$', id_):
        # scp-000 scp-000-j scp-000-ex
        # scp-cn-000 scp-cn-000-j scp-cn-000-ex
        page = 1
        if '-j' in id_:
            url = 'joke-scps'
        elif '-ex' in id_:
            url = 'scp-ex'
        else:
            url = 'scp-series'
            page = int(primary.group(1)) // 1000 + 1
        url += '-cn' if 'cn-' in id_ else ''
        url += f'-{page}/' if page != 1 else '/'
    elif re.match(r'^[0-9]{3,4}-jp(?:-j)?$', id_):
        url = 'scp-international/'
    else:
        raise InvalidSource(rsn=InvalidSource.Rsn.inp)
    web = fetch_web(url)
    title_e = web.find_all(name='a', text=f'SCP-{id_}', limit=1)[0]
    if not title_e:
        raise InvalidSource(rsn=InvalidSource.Rsn.non)
    return str(title_e.parent)


def fetch_title(base, type_):
    if type_ == ProjType.doc:
        base = re.match(r'^(?:scp-)?(.*)$', base.lower()).group(1)
        source = f'/scp-{base}'
        title = f"SCP-{base.upper()}{re.match('^<li><a.*/a>(.*)</li>$', fetch_title_by_id(base)).group(1)}"
    elif type_ == ProjType.sub:
        if base[0] != '/':
            base = f'/{base}'
        source = base.lower()
        title = fetch_title_by_url(source)
    else:
        base_ = base.split('\n')
        title = base_[0]
        source = base_[1]
    return title, source


def count_chars(source, type_):
    if type_ not in (ProjType.doc, ProjType.sub):
        count = 0
    else:
        web = fetch_web(source)
        page_content = web.find('div', {'id': 'page-content'})

        # TODO: fix text
        text = re.sub(r'ancd' 'x', page_content.text.lower())
        text = re.sub(r'x  (x  )*x', 'xx', re.sub(r'[0-9a-z-]', ' x ', text))
        text = re.sub(r'(?![\u4e00-\u9fa5]|[0-9a-z-]).', ' ', text)
        str_list = re.sub(r'\s+', ' ', text).split(' ')
        count = 0
        for elem in str_list:
            if 'x' in elem:
                count += 1
            else:
                count += len(elem)
    return count


def build_info(base, type_):
    title, source = fetch_title(base, type_)
    words_count = count_chars(source, type_)
    return title, source, words_count


fetch_title_by_id('9009')
