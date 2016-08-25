import datetime
import os
from collections import namedtuple

from django.core.exceptions import ValidationError
from django.test import TestCase

from wizard import models
from ..tools import file_dir

FakeNamedObject = namedtuple('FakeNamedObject', ['name'])

COLUMNS_5 = file_dir(__file__, 'resources', 'columns_5.csv')
COLUMNS_12 = file_dir(__file__, 'resources', 'columns_12.csv')
MATRIX_5_3 = file_dir(__file__, 'resources', 'matrix_5x3.csv')
CHALEARN_DILBERT = file_dir(__file__, 'resources', 'chalearn_small_dilbert')


def create_with_file(clss, file_path, **kwargs):
    """
    Helper class to test ColumXXXX and MatrixXXX classes,
    the one that stores files in their x.raw_content field.

    Handles the file storage.
    """
    c = clss(**kwargs)
    base_name = os.path.basename(file_path)
    with open(file_path, 'r') as f:
        c.raw_content.save(base_name, f)
    c.save()
    return c


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


class TestColumnarStorage(TestCase):
    def test_create_a_columnar_file_sets_the_count_correctly(self):
        c = create_with_file(models.ColumnarTypesDefinition, COLUMNS_5)
        self.assertEqual(c.count, 5)


class TestAxisDescriptionModel(TestCase):
    def test_create_an_axis_description_empty_is_fine(self):
        a = models.AxisDescriptionModel.objects.create()
        self.assertIsNotNone(a)
        self.assertIsNone(a.count)

    def test_create_an_axis_force_count_works(self):
        a = models.AxisDescriptionModel.objects.create(count=64)
        self.assertEqual(a.count, 64)

    def test_create_axis_with_types_works(self):
        c = create_with_file(models.ColumnarTypesDefinition, COLUMNS_5)
        a = models.AxisDescriptionModel.objects.create(types=c)
        self.assertEqual(a.types.count, 5)

    def test_create_axis_with_types_and_names_works(self):
        c_types = create_with_file(models.ColumnarTypesDefinition, COLUMNS_5)
        c_names = create_with_file(models.ColumnarNamesDefinition, COLUMNS_5)
        a = models.AxisDescriptionModel.objects.create(types=c_types, names=c_names)

        self.assertEqual(a.types.count, 5)
        self.assertEqual(a.names.count, 5)
        self.assertEqual(a.count, 5)

    def test_create_axis_with_incompatible_columns_fails(self):
        c_types = create_with_file(models.ColumnarTypesDefinition, COLUMNS_5)
        c_names = create_with_file(models.ColumnarNamesDefinition, COLUMNS_12)

        try:
            models.AxisDescriptionModel.objects.create(types=c_types, names=c_names)
            self.fail('creating the axis with different columns sizes should fail.')
        except ValidationError as e:
            self.assertTrue(True)


class TestMatrixStorage(TestCase):
    def test_create_a_matrix_file_sets_the_count_correctly(self):
        m = create_with_file(models.MatrixModel, MATRIX_5_3)
        self.assertEqual(m.rows.count, 5)
        self.assertEqual(m.cols.count, 3)

    def test_matrix_with_invalid_columns_fails(self):
        c = create_with_file(models.ColumnarTypesDefinition, COLUMNS_12)
        a = models.AxisDescriptionModel(types=c)

        try:
            m = create_with_file(models.MatrixModel, MATRIX_5_3, cols=a)
            self.fail('creating the matrix with wrong columns (12 vs 5) should fail.')
        except ValidationError as e:
            self.assertTrue(True)


class TestDatasetModel(TestCase):
    def test_create_a_public_empty_dataset(self):
        d = models.DatasetModel.objects.create(owner=None, is_public=True, name='An empty dataset')

        self.assertIsNotNone(d)
        self.assertFalse(d.is_ready)


class TestTaskModel(TestCase):
    def test_create_an_empty_task(self):
        t = models.TaskModel.objects.create(owner=None, is_public=True, name='An empty task')

        self.assertIsNotNone(t)
        self.assertFalse(t.is_ready)

    def test_feed_a_task_with_train(self):
        m = create_with_file(models.MatrixModel, CHALEARN_DILBERT + '/dilbert_train.data')
        t = models.TaskModel.objects.create(owner=None, is_public=True, name='A simple task',
                                            input_train=m)

        self.assertIsNotNone(t.input_train)
        self.assertFalse(t.is_ready)

    def test_feed_a_task_with_train_valid_test(self):
        m_train = create_with_file(models.MatrixModel, CHALEARN_DILBERT + '/dilbert_train.data')
        m_train_target = create_with_file(models.MatrixModel,
                                          CHALEARN_DILBERT + '/dilbert_train.solution')

        m_test = create_with_file(models.MatrixModel, CHALEARN_DILBERT + '/dilbert_test.data')
        m_valid = create_with_file(models.MatrixModel,
                                   CHALEARN_DILBERT + '/dilbert_valid.data')

        t = models.TaskModel.objects.create(owner=None, is_public=True, name='A simple task',
                                            input_train=m_train, target_train=m_train_target,
                                            input_test=m_test, input_valid=m_valid)

        self.assertTrue(t.is_ready)

    def test_create_a_task_from_chalearn(self):
        t = models.TaskModel.from_chalearn(CHALEARN_DILBERT, 'chalearn - dilbert')

        self.assertIsNotNone(t)
        self.assertTrue(t.is_ready)
        self.assertEqual(t.input_train.rows.count, 10)
        self.assertEqual(t.input_test.rows.count, 5)
        self.assertEqual(t.input_valid.rows.count, 3)
