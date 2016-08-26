import datetime

import pytest

from tests.wizard.tools import (CHALEARN_SAMPLE,
                                CHALEARN_SAMPLE_SPARSE)
from wizard import models
from .tools import create_with_file, FakeNamedObject

pytestmark = pytest.mark.django_db


class TestTools:
    def test_load_info_file(self):
        f = models.load_info_file(CHALEARN_SAMPLE_SPARSE + '/sparse_public.info')

        assert f.getboolean('is_sparse')
        assert f.get('name') == 'sparse'
        assert f.getint('target_num') == 20


class TestStorageTools:
    def test_unique_name_contains_year_month_day(self):
        f = models.StorageNameFactory('some', 'prefix')
        x = f(FakeNamedObject(name='column_kind'), 'my_filename.csv')
        now = datetime.datetime.now()

        assert 'some/prefix' in x
        assert 'my_filename' in x
        assert '.csv' in x
        assert '/column_kind/' in x
        assert '/%04d/' % now.year in x
        assert '/%02d/' % now.month in x
        assert '/%02d/' % now.day in x


class TestTaskModel:
    def test_create_an_empty_task(self):
        t = models.TaskModel.objects.create(owner=None, is_public=True, name='An empty task')

        assert t is not None
        assert not t.is_ready

    def test_feed_a_task_with_train(self):
        m = create_with_file(models.MatrixModel, CHALEARN_SAMPLE + '/adult_train.data')
        t = models.TaskModel.objects.create(owner=None, is_public=True, name='A simple task',
                                            input_train=m)

        assert t.input_train is not None
        assert not t.is_ready

    def test_feed_a_task_with_train_valid_test(self):
        m_train = create_with_file(models.MatrixModel, CHALEARN_SAMPLE + '/adult_train.data')
        m_train_target = create_with_file(models.MatrixModel,
                                          CHALEARN_SAMPLE + '/adult_train.solution')

        m_test = create_with_file(models.MatrixModel, CHALEARN_SAMPLE + '/adult_test.data')
        m_valid = create_with_file(models.MatrixModel,
                                   CHALEARN_SAMPLE + '/adult_valid.data')

        t = models.TaskModel.objects.create(owner=None, is_public=True, name='A simple task',
                                            input_train=m_train, target_train=m_train_target,
                                            input_test=m_test, input_valid=m_valid)

        assert t.is_ready
