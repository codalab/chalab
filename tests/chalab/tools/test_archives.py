from chalab.tools import archives
from chalab.tools import fs

EXAMPLE_FILES = ["README.txt",
                 "mydataset.data",
                 "mydataset.solution",
                 "mydataset_feat.name",
                 "mydataset_info.m",
                 "mydataset_label.name",
                 "mydataset_sample.name"]


def test_extract_zip_file():
    with open('tests/wizard/resources/uploadable/automl_example.zip', 'rb') as f:
        with archives.unzip_fp(f) as tmp:
            content_path = fs.sole_path(tmp)
            assert set(fs.ls(content_path)) == set(EXAMPLE_FILES)
