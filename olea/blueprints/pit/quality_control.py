from fractions import Fraction
from math import sqrt

from models import Dep

__all__ = ['CheckFailed', 'check_file_meta']


class CheckFailed(BaseException):
    def __init__(self, metainfo, required):
        self.confl = {key: metainfo[key] for key in required}
        self.required = required


def ps_checks(i):
    if 'image' not in i['mime']:
        raise CheckFailed({'mime': 'image'})

    return None


def au_checks(i):
    if 'audio' not in i['mime']:
        raise CheckFailed({'mime': 'audio'})

    required = dict()
    j = i['metainfo']

    if j['bitrate'] < 128:
        required['bitrate'] = '>= 128'

    return required


def ae_checks(i):
    if 'video' not in i['mime']:
        raise CheckFailed({'mime': 'video'})

    required = dict()
    j = i['metainfo']

    if j['audioFormat'] != 'AAC':
        required['audioFormat'] = 'AAC'
    if j['fourCC'] not in ('H264', 'H265'):
        required['fourCC'] = 'H264, H265'
    if j['audioSamplesPerSecond'] < 44100:
        required['audioSamplesPerSecond'] = '>= 44100'
    if j['frameRate'] not in (24, 25):
        required['frameRate'] = '24, 25'
    j['ratio'] = str(Fraction(j['width'], j['height']))
    if j['ratio'] not in ('16/9', '64/27'):
        required['ratio'] = '16/9, 21/9(64/27)'
    j['ppi'] = sqrt(j['width']**2 + j['height']**2) / 15
    if j['ppi'] <= 146.5:
        required['ppi'] = '> 146.5'

    return required


def check_file_meta(dep, i):

    if dep == Dep.ps:
        required = ps_checks(i)

    elif dep == Dep.au:
        required = au_checks(i)

    elif dep == Dep.ae:
        required = ae_checks(i)

    else:
        # prevent unexpected file uploading, should never be called
        raise Exception('Unexpected File Uploading')

    if required:
        raise CheckFailed(i['metainfo'], required)
