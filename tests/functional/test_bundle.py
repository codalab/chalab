import os
import shutil
import time
from contextlib import contextmanager
from os import path
from tempfile import TemporaryDirectory

# Not a submission but we don't check its content yet.
DEFAULT_BASELINE_SUBMISSION = path.abspath('tests/wizard/resources/uploadable/automl_example.zip')


def test_bundle_builder(challenge):
    p = (challenge.to_data().pick_dataset(public=True, name='Chalearn - adult')
         .next()
         .next()
         .pick_metric(public=True, name='r2_metric')
         .next()
         .set({'dev_start_date': '2024-01-01\n',
               'final_start_date': '2028-01-01\n',
               'max_submissions_per_day': 2})
         .next()
         .set({'submission': DEFAULT_BASELINE_SUBMISSION})
         .next()
         .edit().submit()
         .up())

    assert p.definition.is_ready

    p = p.build()
    assert p.complete.build_status in ['Scheduled', 'Started', 'Finished']

    for i in range(5):
        try:
            time.sleep(5)
            p = p.refresh()
            assert p.complete.build_status == 'Finished'
            break
        except AssertionError:
            continue

    assert p.complete.build_status == 'Finished'

    url = p.complete.download_url

    r = p.request('GET', url, stream=True)
    r.raise_for_status()

    with tmp_dir('test_bundler') as d:
        dest = path.join(d, 'bundle.zip')

        with open(dest, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        ed = path.join(d, 'extracted')
        os.mkdir(ed)
        shutil.unpack_archive(dest, ed, 'zip')

        assert 'competition.yaml' in os.listdir(ed)


@contextmanager
def tmp_dir(prefix):
    with TemporaryDirectory(prefix=prefix) as d:
        yield d
