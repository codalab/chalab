import os

from chalab.tools import fs


def test_sole_path():
    with fs.tmp_dir() as p:
        fs.mkdir(p, 'my_dir')
        fs.mkdir(p, 'my_dir', 'my_sub_dir')

        assert fs.ls(fs.sole_path(p)) == ['my_sub_dir']


def test_ls_with_globbing():
    with fs.tmp_dir() as p:
        fs.mkdir(p, 'aa')
        fs.mkdir(p, 'ab')
        fs.mkdir(p, 'ba')
        fs.mkdir(p, 'ca')

        assert fs.ls(p, 'a*', glob=True) == [
            os.path.join(p, 'aa'),
            os.path.join(p, 'ab'),
        ]

        try:
            fs.ls(p, 'a*', glob=False)
            assert False, "should fail"
        except FileNotFoundError:
            assert True
