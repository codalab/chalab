def test_flow_create_dataset(challenge):
    p = challenge

    p = p.to_data()
    assert p.is_picker

    p = p.do_create(name="my first created dataset by hand")
    assert p.is_editor

    # TODO
    # p = p.submit(auto_ml_file='./tests/wizard/resources/automl_dataset_basic.zip')
    # assert p.is_editor
    # assert p.name == 'my first created dataset by hand'
