import datetime

import pytest
from django.contrib.auth.models import User

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

    def test_chalearn_task_creation(self):
        dataset = models.DatasetModel.from_chalearn(CHALEARN_SAMPLE, 'chalearn - sample')
        task = models.TaskModel.from_chalearn(dataset, CHALEARN_SAMPLE, 'chalearn - task sample')

        assert task.is_ready
        assert task.dataset == dataset


class TestMetricModel:
    def test_create_a_metric_model(self):
        t = models.MetricModel.objects.create(owner=None, is_public=True,
                                              name='my first metric',
                                              is_ready=True,
                                              classification=True,
                                              regression=True)

        assert t is not None
        assert t.is_ready


class TestDocumentationPageModel:
    def test_page_has_title_and_content(self):
        doc = models.DocumentationModel.create()
        t = models.DocumentationPageModel.create(doc=doc,
                                                 title='my title',
                                                 content='lorem ipsum')

        assert t.documentation == doc
        assert t.title == 'my title'
        assert t.content == 'lorem ipsum'


class TestDocumentationModel:
    def test_create_the_default_documentation_model(self):
        t = models.DocumentationModel.objects.create()
        assert t is not None

    def test_default_documentation_contains_3_pages(self):
        t = models.DocumentationModel.create()

        assert len(t.pages) == 3


class TestChallengeModel:
    def test_challenge_model_has_documentation_field(self):
        user = User.objects.create_user('username', None, 'password')
        t = models.ChallengeModel.objects.create(created_by=user)

        assert t.documentation is None
