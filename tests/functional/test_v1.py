def test_flow_create_dataset(challenge):
    p = challenge

    p = p.to_data()
    assert p.is_picker

    p = p.do_create(name="my first created dataset by hand")
    assert p.is_editor
    assert p.name == 'my first created dataset by hand'

    # TODO
    p.editor_form.submit(automl_upload='./tests/wizard/resources/uploadable/automl_dataset.zip')
    assert p.is_editor
    assert p.is_ready
