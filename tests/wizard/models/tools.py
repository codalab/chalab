import os
from collections import namedtuple


FakeNamedObject = namedtuple('FakeNamedObject', ['name'])

def create_with_file(clss, file_path, **kwargs):
    """
    Helper class to test ColumXXXX and MatrixXXX classes,
    the one that stores files in their x.raw_content field.

    Handles the file storage.
    """
    c = clss(**kwargs)
    base_name = os.path.basename(file_path)
    with open(file_path, 'r') as f:
        c.raw_content.save(base_name, f)
    c.save()
    return c
