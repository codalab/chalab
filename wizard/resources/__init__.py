import os

from chalab.tools import fs


def build_default_scoring(metric, dest):
    p = fs.here(__file__, 'default_scoring')
    fs.copy_dir_content(p, dest)

    path_new = os.path.join(dest, 'libscores.py')
    path_old = os.path.join(dest, 'libscores_tmp.py')

    with open(path_new,'w') as new_file:
        with open(path_old) as old_file:
            for line in old_file:
                if line[:22] == "# Fill with your metric"[:22]:
                    new_file.write("# " + metric.description + "\n")
                    new_file.write(metric.code)
                else:
                    new_file.write(line)

    #Remove original file
    os.remove(path_old)

    with open(os.path.join(dest, 'metric.txt'), 'w') as f:
        print(metric.name, file=f)
