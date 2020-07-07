from config import FE
from config import SITEMAP_FILE


def write_sitemap(body: str):
    with open(SITEMAP_FILE, 'a', encoding=FE) as f:
        f.write(body)
