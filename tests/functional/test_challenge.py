from .test_bundle import DEFAULT_BASELINE_SUBMISSION


def test_flow_with_public_dataset(challenge):
    desc = challenge.challenge

    # I can see the description for my challenge
    d = challenge.description
    assert d.h1.text == desc.title
    assert desc.org_name in d.h3.text
    assert d.content.text == desc.description

    p = challenge
    assert not p.definition.steps.get(clss='data').is_ready
    assert not p.definition.steps.get(clss='task').is_ready

    # I can click on the data page
    p = p.to_data()
    assert p.is_picker

    # I can pick a dataset
    p = p.pick_dataset(public=True, name='Chalearn - adult')
    assert p.is_editor

    # I can move to the metric
    p = p.next()

    # I can go up to the challenge
    p = p.up()

    # The step for the data and metric is marked as complete
    assert p.definition.steps.get(clss='data').is_ready
    assert p.definition.steps.get(clss='task').is_ready


def test_flow_pick_metrics(challenge):
    p = challenge
    assert not p.definition.steps.get(clss='metric').is_ready

    # pick data
    p = p.to_data()
    p = p.pick_dataset(public=True, name='Chalearn - adult')
    p = p.up()
    assert p.is_('wizard', 'challenge')

    # move to metrics
    p = p.to_metric()
    p = p.pick_metric(public=True, name='r2_metric')
    p = p.up()

    assert p.definition.steps.get(clss='metric').is_ready


def test_flow_pick_protocol(challenge):
    p = challenge
    assert not p.definition.steps.get(clss='protocol').is_ready

    # move to protocol
    p = p.to_protocol()
    p = p.set({'dev_start_date': '2024-01-01\n',
               'final_start_date': '2022-01-01\n',
               'max_submissions_per_day': 5,
               'max_submissions': 10})
    p = p.up()

    assert p.definition.steps.get(clss='protocol').is_ready


def test_flow_documentation(challenge):
    p = challenge
    assert not p.definition.steps.get(clss='documentation').is_ready

    # move to documentation
    p = p.to_documentation()

    assert p.pages.get(text='overview').is_active
    assert p.page.title == 'overview'
    assert p.page.content

    # select another page
    p = p.focus('data')

    assert p.pages.get(text='data').is_active
    assert p.page.title == 'data'
    assert p.page.content

    # edit the page
    p = p.edit()
    p = p.submit('this is my new content')

    assert p.page.content == 'this is my new content'


def test_documentation_with_templating(challenge):
    p = (challenge.to_documentation()
         .focus('overview')
         .edit()
         .submit('my challenge: $challenge_title with ${challenge_description}'))

    c = p.challenge
    assert p.page.content == "my challenge: %s with %s" % (c.title, c.description)


def test_complete_flow(challenge):
    p = challenge

    assert not p.definition.is_ready

    p = (p.to_data().pick_dataset(public=True, name='Chalearn - adult')
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
