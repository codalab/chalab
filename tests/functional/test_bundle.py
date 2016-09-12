import time


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
    assert p.complete.build_status == 'Scheduled'

    time.sleep(5)

    p = p.refresh()
    assert p.complete.build_status == 'Finished'
