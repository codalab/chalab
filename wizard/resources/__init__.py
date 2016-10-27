import os

from chalab.tools import fs


def build_default_scoring(name, dest):
    p = fs.here(__file__, 'default_scoring')
    fs.copy_dir_content(p, dest)

    with open(os.path.join(dest, 'metric.info'), 'w') as f:
        print(name, file=f)
