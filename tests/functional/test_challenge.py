def test_flow_with_public_dataset(challenge):
    desc = challenge.challenge

    # I can see the description for my challenge
    j = challenge.jumbotron
    assert j.h1.text == desc.title
    assert j.h3.text == desc.org_name

    assert challenge.description.body.text == desc.description

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
    p = p.pick_metric(public=True, name='log_loss')
    p = p.up()

    assert p.definition.steps.get(clss='metric').is_ready


def test_flow_pick_protocol(challenge):
    p = challenge
    assert not p.definition.steps.get(clss='protocol').is_ready

    # move to protocol
    p = p.to_protocol()
    p = p.set({'end_date': '2024-01-01',
               'allow_reuse': True,
               'publicly_available': True,
               'has_registration': True,
               'max_submissions_per_day': 5,
               'max_submissions': 10,
               'ranked_submissions': True})
    p = p.up()

    assert p.definition.steps.get(clss='protocol').is_ready


def test_flow_documentation(challenge):
    p = challenge
    assert not p.definition.steps.get(clss='documentation').is_ready

    # move to documentation
    p = p.to_documentation()

    assert p.pages.get(text='presentation').is_active
    assert p.page.title == 'presentation'
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
         .focus('presentation')
         .edit()
         .submit('my challenge: $challenge_title with ${challenge_description}'))

    c = p.challenge
    assert p.page.content == "my challenge: %s with %s" % (c.title, c.description)
