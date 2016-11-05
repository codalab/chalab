import os
import shutil
from contextlib import contextmanager
from glob import glob as globbing
from tempfile import TemporaryDirectory


class InvalidDirectoryException(Exception):
    def __init__(self, msg):
        self.message = msg



def sole_path(path):
    l = ls(path)

    if len(l) != 1:
        raise InvalidDirectoryException(
            "Expected a single file/folder in path, got multiple: %s" % l
        )

    return os.path.join(path, l[0])


def ls(*paths, glob=False):
    p = os.path.join(*paths)

    if glob:
        return globbing(p)
    else:
        return os.listdir(p)


def here(__file__, *rest):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        *rest)


def copy_dir_content(dir, dest):
    shutil.copytree(dir, dest)


@contextmanager
def tmp_dir():
    with TemporaryDirectory() as d:
        yield d


def mkdir(*paths):
    os.makedirs(os.path.join(*paths))
