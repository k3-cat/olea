import re

import requests
from bs4 import BeautifulSoup

from models import Proj
from core.errors import InvalidSource
from core.singleton import redis
from core.utils import FromConf

_CN_SITE_URL = 'http://scp-wiki-cn.wikidot.com'
_web_exp = FromConf.load('WEB_EXP')


def fetch_web(url):
    if not (web_page_t := redis.get(f'web-{url}')):
        web_page = requests.get(f'{_CN_SITE_URL}/{url}')
        if web_page.status_code == 404:
            raise InvalidSource(rsn=InvalidSource.Rsn.web, url=url)

        web_page_t = web_page.text
        redis.set(f'web-{url}', web_page_t, ex=_web_exp)

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
    if not (title_e := web.find_all(name='a', text=f'SCP-{id_}', limit=1)[0]):
        raise InvalidSource(rsn=InvalidSource.Rsn.non)

    return str(title_e.parent)


def fetch_title(base, cat):
    if cat == Proj.C.doc:
        base = re.match(r'^(?:scp-)?(.*)$', base.lower()).group(1)
        source = f'/scp-{base}'
        title = (f'SCP-{base.upper()}'
                 f"{re.match(r'^<li><a.*/a>(.*)</li>$', fetch_title_by_id(base)).group(1)}")

    elif cat == Proj.C.sub:
        if base[0] != '/':
            base = f'/{base}'
        source = base.lower()
        title = fetch_title_by_url(source)

    elif cat == Proj.C.ani:
        base_ = base.split('\n')
        title = base_[0]
        source = base_[1]

    else:
        raise Exception('Unexpected CAT')

    return (title, source)


def count_chars(source, cat):
    if cat not in (Proj.C.doc, Proj.C.sub):
        count = 0

    else:
        web = fetch_web(source)
        page_content = web.find('div', {'id': 'page-content'})

        text = page_content.text.lower().replace('\u2588', 'x')
        text = re.sub(r'x  (x  )*x', 'xx', re.sub(r'[0-9a-z-]', ' x ', text))
        text = re.sub(r'(?![\u4e00-\u9fa5]|[0-9a-z-]).', ' ', text)
        str_list = re.sub(r'\s+', ' ', text).split()
        count = 0
        for elem in str_list:
            if 'x' in elem:
                count += 1
            else:
                count += len(elem)

    return count


def build_info(base, cat):
    title, source = fetch_title(base, cat)
    words_count = count_chars(source, cat)
    return (title, source, words_count)
