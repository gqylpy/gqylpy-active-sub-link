from tools import db
from tools import exec_sql


def fetch_blog_path(now_bid: int or str) -> tuple:
    """获取新加入的文章链接"""
    return exec_sql(f'''
        SELECT user.blog_path, blog.id
        FROM user INNER JOIN blog
        ON user.id = blog.user_id
        WHERE blog.id > {now_bid}
          AND blog.is_private IS FALSE 
          AND blog.is_draft IS FALSE 
          AND blog.is_delete IS FALSE 
          AND blog.access_password IS NULL
        ORDER BY blog.id DESC
    ''', database=db.hello_world)
