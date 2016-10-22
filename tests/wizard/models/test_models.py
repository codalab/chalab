import datetime

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

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
        m_valid_target = create_with_file(models.MatrixModel,
                                          CHALEARN_SAMPLE + '/adult_valid.solution')

        t = models.TaskModel.objects.create(owner=None, is_public=True, name='A simple task',
                                            input_train=m_train, target_train=m_train_target,
                                            input_test=m_test,
                                            input_valid=m_valid, target_valid=m_valid_target)

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


class TestProtocolModel:
    def test_can_create(self):
        m = models.ProtocolModel.objects.create(max_submissions_per_day=2)
        assert m is not None

    def test_cant_use_negative_values(self):
        try:
            m = models.ProtocolModel.objects.create(max_submissions_per_day=-2)
            assert False, "should raise"
        except IntegrityError:
            assert True


class TestPhaseModel:
    def test_phase_model_has_name(self):
        user = User.objects.create_user('username', None, 'password')
        t = models.ChallengeModel.objects.create(created_by=user)

        p = t.append_phase(name='my phase x')
        assert p.name == 'my phase x'

    def test_phase_can_be_retrieved(self):
        user = User.objects.create_user('username', None, 'password')
        t = models.ChallengeModel.objects.create(created_by=user)

        p = t.append_phase(name='my phase x')
        assert list(t.phases.all()) == [p]


class TestChallengeModel:
    def test_challenge_model_has_documentation_field(self):
        user = User.objects.create_user('username', None, 'password')
        t = models.ChallengeModel.objects.create(created_by=user)

        assert t.documentation is None

    def test_challenge_model_has_created_an_updated_fields(self):
        user = User.objects.create_user('username', None, 'password')
        t = models.ChallengeModel.objects.create(created_by=user)

        assert t.created_at is not None
        assert t.updated_at is not None

    def test_challenge_model_has_phases_field_defaults(self):
        user = User.objects.create_user('username', None, 'password')
        t = models.ChallengeModel.objects.create(created_by=user)

        t.generate_default_phases()

        assert t.phases.all().count() == 2
