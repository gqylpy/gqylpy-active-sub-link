import time

from .sub_link import sub_link
from .db_oper import fetch_blog_path
from .now_bid_oper import fetch_now_bid
from .now_bid_oper import record_now_bid
from .write_sitemap import write_sitemap

from config import FETCH_NEW_BLOG_INTERVAL

_data_max_length = 2000


def gen_body(data: tuple):
    """生成body数据"""
    body = ''
    for blog_path, bid in data:
        body += f'http://blog.gqylpy.com/{blog_path}/{bid}/\n'
    return body


def split_data(data: tuple):
    a, b = divmod(len(data), _data_max_length)
    tmp = []

    first = 0
    for i in range(1, a + 1):
        last = _data_max_length * i
        tmp.append(data[first: last])
        first = last
    tmp.append(data[first:])

    return tmp


def main():
    while True:
        try:

            # 获取新文章
            while True:
                data = fetch_blog_path(fetch_now_bid())
                if data:
                    break
                time.sleep(FETCH_NEW_BLOG_INTERVAL)

            print(f'新文章数量数: {len(data)}')

            # 提取出当前最大的blog.id
            now_bid = data[0][1]

            # 开始提交链接
            for data in split_data(data):
                body = gen_body(data)

                # 写入sitemap.txt文件
                write_sitemap(body)

                # 提交链接
                status_code, json_data = sub_link(body)

                # 记录当前的bid
                if status_code == 200:
                    record_now_bid(now_bid)

                print(status_code, json_data)

        except Exception as e:
            print(e)
