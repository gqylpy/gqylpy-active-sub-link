import requests
from json.decoder import JSONDecodeError

from config import DOMAIN_NAME
from config import SUBMIT_TOKEN
from config import REQUEST_TIMEOUT

_sub_url = f'http://data.zz.baidu.com/urls?site={DOMAIN_NAME}&token={SUBMIT_TOKEN}'

_headers = {
    'User-Agent': 'curl/7.12.1',
    'Host': 'data.zz.baidu.com',
    'Content-Type': 'text/plain',
    'Content-Length': '83',
}


def sub_link(body: str):
    res = requests.post(
        url=_sub_url,
        headers=_headers,
        data=body,
        timeout=REQUEST_TIMEOUT
    )
    try:
        return res.status_code, res.json()
    except JSONDecodeError as e:
        print(e)
        return res.status_code, None
