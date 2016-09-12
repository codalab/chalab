import os
import shutil
import time
from contextlib import contextmanager
from os import path
from tempfile import TemporaryDirectory


def test_bundle_builder(challenge):
    p = (challenge.to_data().pick_dataset(public=True, name='Chalearn - adult')
         .next()
         .next()
         .pick_metric(public=True, name='log_loss')
         .next()
         .set({'end_date': '2024-01-01',
               'allow_reuse': True,
               'max_submissions_per_day': 2})
         .next()
         .edit().submit()
         .up())

    assert p.definition.is_ready

    p = p.build()
    assert p.complete.build_status in ['Scheduled', 'Started', 'Finished']

    time.sleep(5)

    p = p.refresh()
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
