import os


def gen_path(*args: str) -> 'An absolute path':
    # Generate an absolute path.
    return os.path.abspath(os.path.join(*args))
