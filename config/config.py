import os


def _gen_path(*args: str) -> 'An absolute path':
    # Generate an absolute path.
    return os.path.abspath(os.path.join(*args))


BASE_DIR = _gen_path(os.path.dirname(os.path.dirname(__file__)))

DB_DIR = _gen_path(BASE_DIR, 'db')

IN_SERVER = True

# 文件编码
FE = 'UTF-8'

REQUEST_TIMEOUT = 30

FETCH_NEW_BLOG_INTERVAL = 60 * 1

# 提交链接携带的token
SUBMIT_TOKEN = 'tek0boTIxtWMOi4q'

DOMAIN_NAME = 'blog.gqylpy.com'

SITEMAP_FILE = '/data/hello_world/static/sitemap.txt'
