import datetime

from django.test import TestCase

from tests.wizard.tools import (CHALEARN_SAMPLE,
                                CHALEARN_SAMPLE_SPARSE)
from wizard import models
from .tools import create_with_file, FakeNamedObject


class TestTools(TestCase):
    def test_load_info_file(self):
        f = models.load_info_file(CHALEARN_SAMPLE_SPARSE + '/sparse_public.info')

        self.assertTrue(f.getboolean('is_sparse'))
        self.assertEqual(f.get('name'), 'sparse')
        self.assertEqual(f.getint('target_num'), 20)


class TestStorageTools(TestCase):
    def test_unique_name_contains_year_month_day(self):
        f = models.StorageNameFactory('some', 'prefix')
        x = f(FakeNamedObject(name='column_kind'), 'my_filename.csv')
        now = datetime.datetime.now()

        self.assertIn('some/prefix', x)
        self.assertIn('my_filename', x)
        self.assertIn('.csv', x)
        self.assertIn('/column_kind/', x)
        self.assertIn('/%04d/' % now.year, x)
        self.assertIn('/%02d/' % now.month, x)
        self.assertIn('/%02d/' % now.day, x)


class TestTaskModel(TestCase):
    def test_create_an_empty_task(self):
        t = models.TaskModel.objects.create(owner=None, is_public=True, name='An empty task')

        self.assertIsNotNone(t)
        self.assertFalse(t.is_ready)

    def test_feed_a_task_with_train(self):
        m = create_with_file(models.MatrixModel, CHALEARN_SAMPLE + '/adult_train.data')
        t = models.TaskModel.objects.create(owner=None, is_public=True, name='A simple task',
                                            input_train=m)

        self.assertIsNotNone(t.input_train)
        self.assertFalse(t.is_ready)

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

        self.assertTrue(t.is_ready)
