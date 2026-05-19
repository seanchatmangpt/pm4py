import gzip
import os
import shutil
import tempfile
from contextlib import contextmanager


def is_gzip_path(file_path: str) -> bool:
    return str(file_path).lower().endswith(".gz")


def open_text(file_path: str, mode: str, encoding: str):
    if is_gzip_path(file_path):
        return gzip.open(file_path, mode=mode, encoding=encoding)
    return open(file_path, mode=mode, encoding=encoding)


def open_binary(file_path: str, mode: str):
    if is_gzip_path(file_path):
        return gzip.open(file_path, mode=mode)
    return open(file_path, mode=mode)


def get_uncompressed_suffix(file_path: str) -> str:
    path = str(file_path)
    if is_gzip_path(path):
        path = path[:-3]
    _, suffix = os.path.splitext(path)
    return suffix or ".tmp"


@contextmanager
def decompressed_path(file_path: str):
    if not is_gzip_path(file_path):
        yield file_path
        return

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=get_uncompressed_suffix(file_path)
    )
    tmp.close()

    try:
        with gzip.open(file_path, "rb") as source:
            with open(tmp.name, "wb") as target:
                shutil.copyfileobj(source, target)
        yield tmp.name
    finally:
        os.remove(tmp.name)
