from chalab.tools import archives
from chalab.tools import fs

EXAMPLE_FILES = ["README.txt",
                 "automl_dataset.data",
                 "automl_dataset.solution",
                 "automl_dataset_feat.name",
                 "automl_dataset_info.m",
                 "automl_dataset_label.name",
                 "automl_dataset_sample.name"]


def test_extract_zip_file():
    with open('tests/wizard/resources/uploadable/automl_dataset.zip', 'rb') as f:
        with archives.unzip_fp(f) as tmp:
            content_path = fs.sole_path(tmp)
            assert set(fs.ls(content_path)) == set(EXAMPLE_FILES)
