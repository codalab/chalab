import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from tests.wizard.tools import (COLUMNS_5, COLUMNS_12, MATRIX_5_3, CHALEARN_SAMPLE,
                                CHALEARN_SAMPLE_SPARSE,
                                CHALEARN_SAMPLE_WITHOUT_FEAT_SPEC, CHALEARN_SAMPLE_WRONG_FEAT_SPEC,
                                CHALEARN_SAMPLE_WRONG_ROWS)
from wizard import models
from .tools import create_with_file

pytestmark = pytest.mark.django_db


class TestColumnarStorage:
    def test_create_a_columnar_file_sets_the_count_correctly(self):
        c = create_with_file(models.ColumnarTypesDefinition, COLUMNS_5)
        assert c.count == 5


class TestAxisDescriptionModel:
    def test_create_an_axis_description_empty_is_fine(self):
        a = models.AxisDescriptionModel.create()

        assert a is not None
        assert a.count is None

    def test_create_an_axis_force_count_works(self):
        a = models.AxisDescriptionModel.create(count=64)

        assert a.count == 64

    def test_create_axis_with_types_works(self):
        c = create_with_file(models.ColumnarTypesDefinition, COLUMNS_5)
        a = models.AxisDescriptionModel.create(types=c)

        assert a.types.count == 5

    def test_create_axis_with_types_and_names_works(self):
        c_types = create_with_file(models.ColumnarTypesDefinition, COLUMNS_5)
        c_names = create_with_file(models.ColumnarNamesDefinition, COLUMNS_5)
        a = models.AxisDescriptionModel.create(types=c_types, names=c_names)

        assert a.types.count == 5
        assert a.names.count == 5
        assert a.count == 5

    def test_create_axis_with_incompatible_columns_fails(self):
        c_types = create_with_file(models.ColumnarTypesDefinition, COLUMNS_5)
        c_names = create_with_file(models.ColumnarNamesDefinition, COLUMNS_12)

        try:
            models.AxisDescriptionModel.objects.create(types=c_types, names=c_names)
            assert False, 'creating the axis with different columns sizes should fail.'
        except ValidationError:
            assert True


class TestMatrixStorage:
    def test_create_a_matrix_file_sets_the_count_correctly(self):
        m = create_with_file(models.MatrixModel, MATRIX_5_3)

        assert m.rows.count == 5
        assert m.cols.count == 3

    def test_matrix_with_invalid_columns_fails(self):
        c = create_with_file(models.ColumnarTypesDefinition, COLUMNS_12)
        a = models.AxisDescriptionModel(types=c)

        try:
            create_with_file(models.MatrixModel, MATRIX_5_3, cols=a)
            assert False, 'creating the matrix with wrong columns (12 vs 5) should fail.'
        except ValidationError:
            assert True

    def test_sparse_matrix_doesnt_fail_when_columns_count_do_not_match(self):
        c = create_with_file(models.ColumnarTypesDefinition,
                             CHALEARN_SAMPLE_SPARSE + '/sparse_feat.type')
        a = models.AxisDescriptionModel(types=c)

        m = create_with_file(models.MatrixModel, CHALEARN_SAMPLE_SPARSE + '/sparse.data',
                             cols=a, is_sparse=True)

        assert m.rows.count == 15
        assert m.cols.count == 61188


class TestDatasetModel:
    def test_create_a_public_empty_dataset(self):
        d = models.DatasetModel.create('An empty dataset', is_public=True)

        assert d is not None
        assert not d.is_ready

    def test_available_is_empty_by_default(self):
        user = User.objects.create_user('username', None, 'password')
        assert models.DatasetModel.available(user) == []

    def test_create_a_dataset_shows_up_for_user(self):
        user = User.objects.create_user('username', None, 'password')
        d = models.DatasetModel.create('Some dataset', owner=user)

        assert models.DatasetModel.available(user) == [d]

    def test_public_dataset_shows_up_for_user(self):
        user = User.objects.create_user('username', None, 'password')
        d = models.DatasetModel.create('Some dataset', owner=None, is_public=True)

        assert models.DatasetModel.available(user) == [d]

    def test_chalearn_dataset_creation(self):
        t = models.DatasetModel.from_chalearn(CHALEARN_SAMPLE, 'chalearn - sample')

        assert t is not None
        assert t.is_ready
        assert t.input.rows.count == 15
        assert t.target.rows.count == 15

    def test_chalearn_wrong_rows_fails(self):
        try:
            models.DatasetModel.from_chalearn(CHALEARN_SAMPLE_WRONG_ROWS,
                                              'chalearn - sample wrong rows')
            assert False, "This should be invalid"
        except ValidationError:
            assert True

    def test_chalearn_wrong_feat_spec_fails(self):
        try:
            models.DatasetModel.from_chalearn(CHALEARN_SAMPLE_WRONG_FEAT_SPEC,
                                              'chalearn - sample wrong feat spec')
            assert False, "This should be invalid"
        except ValidationError:
            assert True

    def test_chalearn_without_feat_spec_fails(self):
        t = models.DatasetModel.from_chalearn(CHALEARN_SAMPLE_WITHOUT_FEAT_SPEC,
                                              'chalearn - sample without feat spec')

        assert t.is_ready

    def test_chalearn_with_sparse_doesnt_fail(self):
        t = models.DatasetModel.from_chalearn(CHALEARN_SAMPLE_SPARSE,
                                              'chalearn - sample sparse')
        assert t.is_ready
