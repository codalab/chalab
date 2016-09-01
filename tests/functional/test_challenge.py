def test_flow_with_public_dataset(challenge):
    desc = challenge.challenge

    # I can see the description for my challenge
    j = challenge.jumbotron
    assert j.h1.text == desc.title
    assert j.h3.text == desc.org_name

    assert challenge.description.body.text == desc.description

    # I can click on the data page
    p = challenge.to_data()
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

