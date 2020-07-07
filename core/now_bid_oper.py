from tools import gen_path

from config import FE
from config import DB_DIR

_now_bid = gen_path(DB_DIR, 'now_bid')


def fetch_now_bid():
    with open(_now_bid, 'r', encoding=FE) as fp:
        return fp.read()


def record_now_bid(now_bid: str or int):
    with open(_now_bid, 'w', encoding=FE) as fp:
        fp.write(str(now_bid))
