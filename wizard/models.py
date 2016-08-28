import logging
import os
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
        return len(line.split())
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


import re

FIELD_PARSER = re.compile('(\S+)\s*=\s*(\S.*\S?)\s*')


class InfoFile(object):
    """
    A simple key = value file representation.
    Deals with info files such as:
    ```
    my_field = 'my string value'
    my_second_field = 42
    ```

    mimick the config parser format as close as possible.
    """

    def __init__(self, lines):
        self._fields = dict([self.parse_field(line) for line in lines if line.strip()])

    def getint(self, name):
        return int(self._fields[name])

    def getboolean(self, name):
        try:
            return bool(self.getint(name))
        except ValueError:
            return bool(self.get(name))

    def get(self, name):
        return self._fields[name]

    @staticmethod
    def parse_field(line):
        m = re.match(FIELD_PARSER, line)

        if m is None:
            raise Exception("Line couldn't be parsed: %s" % (line,))

        x, y = m.groups()

        if y.startswith('\''):
            assert y.endswith('\''), "Field %s = %s is weirdly formatted (quotes)" % (x, y)
            y = y[1:-1]

        return x, y


def load_info_file(file):
    """
    Load a Chalearn config file using a custom format.

    Note the format used looks like an ini file, with no headers.
    However the quoting around string values makes configparser useless.
    """
    with open(file, 'r') as f:
        try:
            return InfoFile(f.readlines())
        except Exception as e:
            raise Exception("Problem loading: %s" % file) from e


class MatrixModel(models.Model):
    name = 'matrix'

    raw_content = models.FileField(upload_to=StorageNameFactory('data', 'raw', 'matrix'))
    is_sparse = models.BooleanField(default=False, null=False)

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

        if not self.is_sparse:
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

    input = OneToOneField(MatrixModel, null=True, related_name='dataset_input')
    target = OneToOneField(MatrixModel, null=True, related_name='dataset_target')

    @classmethod
    def from_chalearn(cls, path, name, owner=None, is_public=True):
        try:
            i = load_info_file(chalearn_path(path, '_public.info'))
            is_sparse = i.getboolean('is_sparse')
        except FileNotFoundError:
            is_sparse = False

        input = load_chalearn(path, '.data', is_sparse=is_sparse)

        try:
            cols_type = load_chalearn(path, '_feat.type', clss=ColumnarTypesDefinition)
            input.cols.types = cols_type
            input.save()
        except FileNotFoundError:
            pass  # It's fine, feat specs are not mandatory.

        return cls.objects.create(
            owner=owner, is_public=is_public, name=name,
            input=input,
            target=load_chalearn(path, '.solution')
        )

    def clean(self):
        super().clean()

        might_be_ready = self.input is not None and self.target is not None

        if might_be_ready:
            if self.input.rows.count != self.target.rows.count:
                raise ValidationError('The number of rows in the input and target do not match')

            self.is_ready = True

    def save(self, *args, **kwargs):
        self.clean()  # Force clean on save.
        super().save(*args, **kwargs)

    def __str__(self):
        return "<%s: \"%s\"; ready=%s>" % (type(self).__name__, self.name, self.is_ready)


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


def chalearn_path(path, suffix):
    name = path.split('/')[-1]
    p = os.path.join(path, '%s%s' % (name, suffix))
    return p


def load_chalearn(path, suffix, clss=MatrixModel, **kwargs):
    return create_with_file(clss, chalearn_path(path, suffix), **kwargs)


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


class ChallengeModel(models.Model):
    title = models.CharField(max_length=60)
    organization_name = models.CharField(max_length=80)
    description = models.TextField(max_length=255)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    dataset = models.ForeignKey(DatasetModel, null=True)

    def get_absolute_url(self):
        return reverse('wizard:challenge', kwargs={'pk': self.pk})
