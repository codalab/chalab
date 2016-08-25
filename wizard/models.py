import logging
import os
from glob import glob
from time import gmtime, strftime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage
from django.db import models
from django.db.models import OneToOneField
from django.urls import reverse
from django.utils.deconstruct import deconstructible

log = logging.getLogger('wizard/models')

storage = DefaultStorage()


class ChallengeModel(models.Model):
    title = models.CharField(max_length=60)
    organization_name = models.CharField(max_length=80)
    description = models.TextField(max_length=255)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('wizard:challenge', kwargs={'pk': self.pk})


class ChallengeDataModel(models.Model):
    challenge = models.ForeignKey(ChallengeModel, on_delete=models.CASCADE, related_name='data')
    name = models.CharField(max_length=80, default="")

    K_CHALEARN_ADULT = 'chalearn/adult'
    K_CHALEARN_ALEXIS = 'chalearn/alexis'
    K_CHALEARN_CHRISTINE = 'chalearn/christine'
    K_CHALEARN_DILBERT = 'chalearn/dilbert'
    K_CHALEARN_DOROTHEA = 'chalearn/dorothea'
    K_CHALEARN_FABERT = 'chalearn/fabert'
    K_CHALEARN_JANNIS = 'chalearn/jannis'
    K_CHALEARN_MADELINE = 'chalearn/madeline'

    DATA_SET_KIND = [
        (K_CHALEARN_ADULT, 'Chalearn: Adult'),
        (K_CHALEARN_ALEXIS, 'Chalearn: Alexis'),
        (K_CHALEARN_CHRISTINE, 'Chalearn: Christine'),
        (K_CHALEARN_DILBERT, 'Chalearn: Dilbert'),
        (K_CHALEARN_DOROTHEA, 'Chalearn: Dorothea'),
        (K_CHALEARN_FABERT, 'Chalearn: Fabert'),
        (K_CHALEARN_JANNIS, 'Chalearn: Jannis'),
        (K_CHALEARN_MADELINE, 'Chalearn: Madeline'),
    ]

    kind = models.CharField(choices=DATA_SET_KIND, max_length=30, default=K_CHALEARN_ADULT)

    def get_absolute_url(self):
        return reverse('wizard:data', kwargs={'pk': self.challenge.pk})


@deconstructible
class StorageNameFactory(object):
    """
    A factory that will produce a unique filename,
    prefixed by the suffix and the current year/month/day.

    This function is to be used with the Django upload_to in FileField.

    We define a deconstructible instance so that the object can be "serialized" by
    the migration framework.
    """

    def __init__(self, *prefix):
        self.prefix = prefix

    def __call__(self, instance, filename):
        try:
            base = os.path.join(*self.prefix, instance.name, '%Y', '%m', '%d', filename)
            base = strftime(base, gmtime())
            return storage.get_available_name(base)
        except TypeError as e:
            raise TypeError("You probably forgot to define the local `name' field.") from e


def lines_count(file_field):
    """
    Return the number of lines in a django Model FileField.
    """
    try:
        file_field.open('r')
        r = 0
        while file_field.readline():
            r += 1
        return r
    finally:
        file_field.close()


def columns_count_first_line(file_field):
    """
    Return the number of columns for the first line of a file
    from a django Model FileField.
    """
    try:
        file_field.open('r')
        line = file_field.readline()
        return len(line.split(' '))
    finally:
        file_field.close()


class ColumnarFileModel(models.Model):
    name = None

    raw_content = models.FileField(upload_to=StorageNameFactory('data', 'raw', 'columns'))
    count = models.IntegerField()

    def save(self, *args, **kwargs):
        self.count = lines_count(self.raw_content)
        super(ColumnarFileModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class ColumnarTypesDefinition(ColumnarFileModel):
    name = 'types'


class ColumnarNamesDefinition(ColumnarFileModel):
    name = 'names'


class ColumnarDocDefinition(ColumnarFileModel):
    name = 'doc'


class AxisDescriptionModel(models.Model):
    count = models.IntegerField(null=True)

    types = OneToOneField(ColumnarTypesDefinition,
                          null=True, on_delete=models.SET_NULL, related_name='axis')
    names = OneToOneField(ColumnarNamesDefinition,
                          null=True, on_delete=models.SET_NULL, related_name='axis')
    doc = OneToOneField(ColumnarDocDefinition,
                        null=True, on_delete=models.SET_NULL, related_name='axis')

    def clean(self):
        super().clean()

        # Check that this object and the nested objects all share the same counts.
        c1 = self.types.count if self.types is not None else None
        c2 = self.names.count if self.names is not None else None
        c3 = self.doc.count if self.doc is not None else None

        self.count = self.count or c1 or c2 or c3

        if not (c1 == self.count or c1 is None):
            raise ValidationError("the size of the `types' data "
                                  "doesn't match the others definitions.")
        if not (c2 == self.count or c2 is None):
            raise ValidationError("the size of the `names' data "
                                  "doesn't match the others definitions.")
        if not (c3 == self.count or c3 is None):
            raise ValidationError("the size of the `doc' data "
                                  "doesn't match the others definitions.")

    def save(self, *args, **kwargs):
        self.clean()  # Force clean on save.
        super().save(*args, **kwargs)


class MatrixModel(models.Model):
    name = 'matrix'

    raw_content = models.FileField(upload_to=StorageNameFactory('data', 'raw', 'matrix'))

    cols = OneToOneField(AxisDescriptionModel, null=True,
                         on_delete=models.PROTECT, related_name='matrix_cols')
    rows = OneToOneField(AxisDescriptionModel, null=True,
                         on_delete=models.PROTECT, related_name='matrix_rows')

    def clean(self):
        super().clean()  # Called last since we set the default self.columns and self.rows before.

        # TODO(laurent): Validate the file by checking the number of column for EVERY lines.
        rows = lines_count(self.raw_content)
        cols = columns_count_first_line(self.raw_content)

        if self.cols is None:
            self.cols = AxisDescriptionModel()
        if self.rows is None:
            self.rows = AxisDescriptionModel()

        self.cols.count = cols
        self.rows.count = rows

        self.cols.save()
        self.rows.save()

    def save(self, *args, **kwargs):
        self.clean()  # Force clean on save.
        super().save(*args, **kwargs)


class DatasetModel(models.Model):
    owner = models.ForeignKey(User, null=True)
    is_public = models.BooleanField(default=False, null=False)
    is_ready = models.BooleanField(default=False, null=False)
    name = models.CharField(max_length=256, null=False)


def create_with_file(clss, file_path, **kwargs):
    """
    Helper class to test ColumXXXX and MatrixXXX classes,
    the one that stores files in their x.raw_content field.

    Handles the file storage.
    """
    try:
        c = clss(**kwargs)
        base_name = os.path.basename(file_path)
        with open(file_path, 'r') as f:
            c.raw_content.save(base_name, f)
            c.save()
        return c
    except Exception as e:
        log.error("Problem creating from file: clss=%r, path=%s\n%e", clss, file_path, e)
        raise e


def load_chalearn(path, suffix):
    p = glob(os.path.join(path, '*' + suffix))
    assert len(p) == 1, "Invalid chalearn: path=%s, suffix=%s, found=%s" % (path, suffix, p)

    return create_with_file(MatrixModel, p[0])


class TaskModel(models.Model):
    owner = models.ForeignKey(User, null=True)
    is_public = models.BooleanField(default=False, null=False)
    is_ready = models.BooleanField(default=False, null=False)
    name = models.CharField(max_length=256, null=False)

    # TODO(laurent): This pattern of having a sinble model reference by many fields
    # is not viable. We should define a model instance per use case (training, etc).
    # Similar to what we do for the columnar storage model.
    input_train = OneToOneField(MatrixModel, null=True, related_name='model_trained')
    target_train = OneToOneField(MatrixModel, null=True, related_name='model_trained_target')
    input_test = OneToOneField(MatrixModel, null=True, related_name='model_tested')
    input_valid = OneToOneField(MatrixModel, null=True, related_name='model_validated')

    @classmethod
    def from_chalearn(cls, path, name, owner=None, is_public=True):
        return cls.objects.create(
            owner=owner, is_public=is_public, name=name,
            input_train=load_chalearn(path, 'train.data'),
            target_train=load_chalearn(path, 'train.solution'),
            input_test=load_chalearn(path, 'test.data'),
            input_valid=load_chalearn(path, 'valid.data')
        )

    def clean(self):
        super().clean()

        # TODO(laurent): there are some subtleties on the validation
        # regarding nested fields. We also do not need to duplicate
        # the metadata for the columns between each input.
        self.is_ready = (self.input_test is not None and
                         self.target_train is not None and
                         self.input_test is not None and
                         self.input_valid is not None)

    def save(self, *args, **kwargs):
        self.clean()  # Force clean on save.
        super().save(*args, **kwargs)
