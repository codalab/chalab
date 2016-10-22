import os
from contextlib import contextmanager
from glob import glob as globbing
from tempfile import TemporaryDirectory


def sole_path(path):
    l = ls(path)
    assert len(l) == 1
    return os.path.join(path, l[0])


def ls(*paths, glob=False):
    p = os.path.join(*paths)

    if glob:
        return globbing(p)
    else:
        return os.listdir(p)


@contextmanager
def tmp_dir():
    with TemporaryDirectory() as d:
        yield d


def mkdir(*paths):
    os.makedirs(os.path.join(*paths))
