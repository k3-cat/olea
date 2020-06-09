from fractions import Fraction
from math import sqrt

from models import Dep
from olea.errors import DoesNotMeetRequirements


class CheckFailed(BaseException):
    def __init__(self, metadata, required):
        confl = {key: metadata[key] for key in required}
        super().__init__(confl=confl, required=required)


def check_file_meta(dep, i):
    required = dict()
    j = i['metainfo']

    if dep == Dep.ps:
        if 'image' not in i['mime']:
            raise CheckFailed({'mime': 'image'})

    elif dep == Dep.au:
        if 'audio' not in i['mime']:
            raise CheckFailed({'mime': 'audio'})

        if i['audio']['bitrate'] < 128:
            required['bitrate'] = '>= 128'

    elif dep == Dep.ae:
        if 'video' not in i['mime']:
            raise CheckFailed({'mime': 'video'})

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

    else:
        # prevent unexpected file uploading, should never be run
        raise Exception('Unexpected File Uploading')

    if required:
        raise CheckFailed(required)
