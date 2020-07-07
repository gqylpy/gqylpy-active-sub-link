from core import gen_body
from core import fetch_blog_path

from config import FE
from config import SITEMAP_FILE

if __name__ == '__main__':
    data = fetch_blog_path(0)

    body = gen_body(data)

    with open(SITEMAP_FILE, 'w', encoding=FE) as f:
        f.write(body)
