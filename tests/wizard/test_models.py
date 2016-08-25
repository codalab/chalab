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


def make_with_raw_content(clss, file_path, **kwargs):
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
        c = make_with_raw_content(models.ColumnarTypesDefinition, COLUMNS_5)
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
        c = make_with_raw_content(models.ColumnarTypesDefinition, COLUMNS_5)
        a = models.AxisDescriptionModel.objects.create(types=c)
        self.assertEqual(a.types.count, 5)

    def test_create_axis_with_types_and_names_works(self):
        c_types = make_with_raw_content(models.ColumnarTypesDefinition, COLUMNS_5)
        c_names = make_with_raw_content(models.ColumnarNamesDefinition, COLUMNS_5)
        a = models.AxisDescriptionModel.objects.create(types=c_types, names=c_names)

        self.assertEqual(a.types.count, 5)
        self.assertEqual(a.names.count, 5)
        self.assertEqual(a.count, 5)

    def test_create_axis_with_incompatible_columns_fails(self):
        c_types = make_with_raw_content(models.ColumnarTypesDefinition, COLUMNS_5)
        c_names = make_with_raw_content(models.ColumnarNamesDefinition, COLUMNS_12)

        try:
            models.AxisDescriptionModel.objects.create(types=c_types, names=c_names)
            self.fail('creating the axis with different columns sizes should fail.')
        except ValidationError as e:
            self.assertTrue(True)


class TestMatrixStorage(TestCase):
    def test_create_a_matrix_file_sets_the_count_correctly(self):
        m = make_with_raw_content(models.MatrixModel, MATRIX_5_3)
        self.assertEqual(m.rows.count, 5)
        self.assertEqual(m.cols.count, 3)
