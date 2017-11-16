import os
import shutil
from contextlib import contextmanager
from glob import glob as globbing
from tempfile import TemporaryDirectory


class InvalidDirectoryException(Exception):
    def __init__(self, msg):
        self.message = msg


def sole_path(path):
    """
    :param path: Directory to check
    :return tuple: First value is the path housing the dataset files, Second value is boolean flag for loose dataset.
    """
    l = ls(path)

    if len(l) != 1:
        print("Found multiple directories/files inside temp path.")
        for file_or_dir in l:
            print("File or directory found in temp directory from zip: {}".format(file_or_dir))
        return path, True
    else:
        print("L in sole_path is {}".format(l))
        return os.path.join(path, l[0]), False


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
