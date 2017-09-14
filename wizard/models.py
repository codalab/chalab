import logging
import string
from datetime import datetime
from time import gmtime, strftime

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage
from django.core.validators import validate_slug
from django.db import models
from django.db.models import OneToOneField
from django.db.models import Q
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from tinymce.models import HTMLField

from chalab.tools import archives, fs
from chalab.tools.storage import *
from . import docs

log = logging.getLogger('wizard/models')

storage = DefaultStorage()


def build_absolute_uri(path):
    site = Site.objects.get_current().domain
    url = 'http://{site}{path}'.format(site=site, path=path)
    return url

def delete_all(list):
    for obj in list:
        if obj is not None:
            obj.delete()

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


def columns_count_sparse(file_field):
    maximum = 0

    file_field.open('r')
    lines = file_field.readlines()
    file_field.close()

    try:
        for line in lines:
            list_val = list(map(int, line.split()))
            maximum = max(maximum, max(list_val))
    except:
        return None

    return maximum


def columns_all_the_same_count(file_field, cols):
    file_field.open('r')
    lines = file_field.readlines()
    file_field.close()

    for line in lines:
        if line.strip and len(line.split()) != cols:
            return False
    return True


class ColumnarFileModel(models.Model):
    name = None

    raw_content = models.FileField(upload_to=StorageNameFactory('data', 'raw', 'columns'))
    count = models.IntegerField()

    def __str__(self):
        return "<%s: id=%s>" % (type(self).__name__, self.id)

    def save(self, *args, **kwargs):
        if not('skip_clean' in kwargs and kwargs['skip_clean']):
            self.count = lines_count(self.raw_content)
        elif 'skip_clean' in kwargs:
            kwargs.pop('skip_clean', None)
        super(ColumnarFileModel, self).save(*args, **kwargs)

    # Make a deep copy of herself and return it
    def deep_copy(self):
        from django.core.files import File

        new_self = type(self)(raw_content=File(
            open(self.raw_content.path, 'rb')))

        new_self.name = self.name
        new_self.count = self.count

        kwargs = {'skip_clean': True}
        new_self.save(**kwargs)

        return new_self

    def delete(self):
        try:
            self.raw_content.delete(save=False)
        except:
            pass
        super().delete()

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

    def __str__(self):
        return "<%s: id=%s>" % (type(self).__name__, self.id)

    def clean(self):
        super().clean()

        # Check that this object and the nested objects all share the same counts.
        c1 = self.types.count if self.types is not None else None
        c2 = self.names.count if self.names is not None else None

        self.count = self.count or c1 or c2

        if not (c1 == self.count or c1 is None):
            raise ValidationError("the size of the 'types' data "
                                  "doesn't match the others definitions.")
        if not (c2 == self.count or c2 is None):
            raise ValidationError("the size of the 'names' data "
                                  "doesn't match the others definitions.")

    def save(self, *args, **kwargs):
        self.clean()  # Force clean on save.
        super().save(*args, **kwargs)

    @classmethod
    def create(cls, types=None, count=None, names=None):
        x = {}
        if types is not None:
            x['types'] = types
        if count is not None:
            x['count'] = count
        if names is not None:
            x['names'] = names

        return cls.objects.create(**x)

    # Make a deep copy of herself and return it
    def deep_copy(self):
        self.id = None

        self.types = self.types.deep_copy() if self.types is not None else None
        self.names = self.names.deep_copy() if self.names is not None else None
        self.doc = self.doc.deep_copy() if self.doc is not None else None

        self.save()
        return self

    def delete(self):
        delete_all([self.types, self.names, self.doc])
        super().delete()


import re

FIELD_PARSER = re.compile('(\S+)\s*=\s*(\S.*\S?)\s*')


class InfoFile(object):
    """
    A simple key = value file reoverview.
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

    cols = OneToOneField(AxisDescriptionModel, null=True, related_name='matrix_cols')
    rows = OneToOneField(AxisDescriptionModel, null=True, related_name='matrix_rows')

    def __str__(self):
        return "<%s: id=%s>" % (type(self).__name__, self.id)

    def clean(self):
        super().clean()  # Called last since we set the default self.columns and self.rows before.

        rows = lines_count(self.raw_content)

        if self.is_sparse:
            cols = columns_count_sparse(self.raw_content)
        else:
            cols = columns_count_first_line(self.raw_content)

        if not columns_all_the_same_count(self.raw_content, cols) and not self.is_sparse:
            pass
            # raise InvalidAutomlFormatException("Number of cols non coherent in %s" % self.raw_content)

        if self.cols is None:
            self.cols = AxisDescriptionModel.objects.create()
        if self.rows is None:
            self.rows = AxisDescriptionModel.objects.create()

        self.cols.count = cols

        self.rows.count = rows

        self.cols.save()
        self.rows.save()

    def save(self, *args, **kwargs):
        if not('skip_clean' in kwargs and kwargs['skip_clean']):
            self.clean()  # Force clean on save.
        elif 'skip_clean' in kwargs:
            kwargs.pop('skip_clean', None)
        super().save(*args, **kwargs)

    # Make a deep copy of herself and return it
    def deep_copy(self):
        from django.core.files import File

        new_self = MatrixModel(raw_content=File(
            open(self.raw_content.path, 'rb')))

        new_self.name = self.name
        new_self.is_sparse = self.is_sparse

        new_self.cols = self.cols.deep_copy() if self.cols is not None else None
        new_self.rows = self.rows.deep_copy() if self.rows is not None else None

        kwargs = {'skip_clean': True}
        new_self.save(**kwargs)
        return new_self

    def delete(self):
        delete_all([self.cols, self.rows])

        try:
            self.raw_content.delete(save=False)
        except:
            pass

        super().delete()

class InvalidAutomlFormatException(Exception):
    def __init__(self, cause):
        self.cause = cause
        self.message = "Expected an Automl Format archive: " + str(cause)


def default_metric(metric, task):
    suffixes = ['multiclass', 'multilabel', 'binary', 'regression']

    m = metric.split('_')[0]

    if m == 'a':
        m = 'abs'

    name = None
    for s in suffixes:
        if s in task:
            name = '%s_%s' % (m, s)
            break

    if name == 'auc_multiclass':
        print("Skipped missing metric: %s" % (name,))
        return None

    try:
        assert name is not None
        return MetricModel.objects.get(is_public=True, name=name)
    except:
        print("Couldn't find metric for %s" % (name,))
        return None


class DatasetModel(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True)
    is_public = models.BooleanField(default=False, null=False)
    is_ready = models.BooleanField(default=False, null=False)
    name = models.CharField(max_length=256, null=False)
    description = models.TextField(null=True, blank=True, default=None)
    preparation = models.TextField(null=True, blank=True, default=None)
    license = models.CharField(max_length=256, null=True, blank=True, default=None)

    keywords = models.CharField(max_length=256, default="", blank=True)
    authors = models.CharField(max_length=256, default="", blank=True)

    resource_created = models.DateField(null=True, blank=True, default=None)
    resource_url = models.URLField(null=True, blank=True, default=None)
    contact_name = models.CharField(max_length=256, null=True, blank=True, default=None)
    contact_url = models.URLField(max_length=256, null=True, blank=True, default=None)

    default_metric = models.ForeignKey('MetricModel', null=True, blank=True, on_delete=models.SET_NULL)

    fixed_split = models.BooleanField(default=False, null=False)

    input = OneToOneField(MatrixModel, null=True, related_name='dataset_input')
    target = OneToOneField(MatrixModel, null=True, related_name='dataset_target')

    def __str__(self):
        return "<%s: \"%s\"; id=%s; ready=%s>" % (type(self).__name__, self.name, self.id, self.is_ready)

    @classmethod
    def available(cls, user):
        """Return datasets available to a given user."""
        return list(cls.objects.filter(Q(is_public=True) | Q(owner=user)).all())

    @property
    def template_mapping(self):
        return {'dataset_name': self.name}

    @property
    def template_doc(self):
        return {'dataset_name': ''}

    def update_from_chalearn(self, fp_zip):
        with archives.unzip_fp(fp_zip) as d:
            try:
                root = fs.sole_path(d)
                name = os.path.basename(root)

                content = set(x for x in os.listdir(root))

                extensions = ['data', 'solution']
                parts = ['train', 'valid', 'test']
                meta = ['feat.name', 'label.name',
                        'feat.type', 'label.type', 'public.info']

                necessary_wanted = set('%s.%s' % (name, x) for x in extensions)

                pre_split_wanted = set('%s_%s.%s' % (name, p, x)
                                       for x in extensions for p in parts)

                meta_optional = set('%s_%s' % (name, m) for m in meta)

                total_dataset = len(necessary_wanted - content) == 0
                pre_split_dataset = len(pre_split_wanted - content) == 0

                if not total_dataset and not pre_split_dataset:
                    raise InvalidAutomlFormatException(
                        str(necessary_wanted - content) + ' are missing')

            except fs.InvalidDirectoryException as e:
                raise InvalidAutomlFormatException(e) from e

            if pre_split_dataset:

                if not total_dataset:
                    # recreate the original .data and .solution (concatenate)
                    for extension in ['data', 'solution']:
                        output_name = '%s.%s' % (name, extension)
                        outfile = open(os.path.join(root, output_name), 'w')
                        for part in ['train', 'valid', 'test']:
                            input_name = '%s_%s.%s' % (name, part, extension)
                            infile = open(os.path.join(root, input_name), 'r')
                            for line in infile:
                                outfile.write(line)
                            infile.close()
                        outfile.close()

                # Add pre split to database
                from django.shortcuts import get_object_or_404
                challenge = get_object_or_404(ChallengeModel, dataset=self.id)
                task = challenge.task
                if task is None:
                    task = TaskModel(owner=self.owner, dataset=self)
                    task.save()
                    challenge.task = task
                    challenge.save()
                task.update_from_chalearn(root)

            input, target, metric, description = self.load_from_automl(root, any_prefix=False)

            self.name = name
            self.input = input
            self.target = target
            self.description = description
            self.fixed_split = pre_split_dataset

            if metric:
                self.default_metric = metric

            self.save()

            return (total_dataset, pre_split_dataset,
                    content - necessary_wanted - pre_split_wanted - meta_optional)

    @classmethod
    def create_from_chalearn(cls, path, name, owner=None, is_public=True):
        input, target, metric, description = cls.load_from_automl(path, any_prefix=False)
        return cls.create(owner=owner,
                          is_public=is_public,
                          name=name, description=description, fixed_split=True,
                          default_metric=metric, input=input, target=target)

    @classmethod
    def load_from_automl(cls, path, any_prefix=False):
        try:
            i = load_info_file(chalearn_path(path, '_public.info'))
            is_sparse = i.getboolean('is_sparse')
            task, metric = i.get('task'), i.get('metric')
            metric = default_metric(metric, task)
        except FileNotFoundError:
            is_sparse = False
            metric = None

        try:
            description = i.get('description')
        except:
            description = None

        input = load_chalearn(path, '.data',
                              is_sparse=is_sparse, any_prefix=any_prefix)

        if os.path.isfile(chalearn_path(path, '_public.info')):
            input.cols.doc = create_with_file(ColumnarDocDefinition, chalearn_path(path, '_public.info'))

        if os.path.isfile(chalearn_path(path, '_feat.type')):
            input.cols.types = create_with_file(ColumnarTypesDefinition, chalearn_path(path, '_feat.type'))

        if os.path.isfile(chalearn_path(path, '_feat.name')):
            input.cols.names = create_with_file(ColumnarNamesDefinition, chalearn_path(path, '_feat.name'))

        try:
            cols_type = load_chalearn(path, '_feat.type',
                                      clss=ColumnarTypesDefinition,
                                      any_prefix=any_prefix)
            input.cols.types = cols_type
        except FileNotFoundError:
            pass  # It's fine, feat specs are not mandatory.

        target = load_chalearn(path, '.solution', any_prefix=any_prefix)

        if os.path.isfile(chalearn_path(path, '_label.type')):
            target.cols.types = create_with_file(ColumnarTypesDefinition, chalearn_path(path, '_label.type'))

        if os.path.isfile(chalearn_path(path, '_label.name')):
            target.cols.names = create_with_file(ColumnarNamesDefinition, chalearn_path(path, '_label.name'))

        input.save()
        target.save()

        return input, target, metric, description

    @classmethod
    def create(cls, name, owner=None, is_public=False, input=None, target=None,
               default_metric=None, description=None, fixed_split=False):
        x = {}
        if input is not None:
            x['input'] = input
        if target is not None:
            x['target'] = target
        if description is not None:
            x['description'] = description

        return cls.objects.create(name=name, owner=owner, is_public=is_public,
                                  default_metric=default_metric,
                                  fixed_split=fixed_split, **x)

    def clean(self):
        super().clean()

        might_be_ready = self.input is not None and self.target is not None

        if might_be_ready:
            try:
                if self.input.rows.count != self.target.rows.count:
                    raise ValidationError('The number of rows in the input and target do not match')
                else:
                    self.is_ready = True
            except AttributeError:
                pass

    def save(self, *args, **kwargs):
        self.clean()  # Force clean on save.
        super().save(*args, **kwargs)

    def delete(self):
        if len(ChallengeModel.objects.filter(dataset=self))<=1:
            delete_all([self.input, self.target])
            super().delete()


def create_with_file(clss, file_path, **kwargs):
    """
    Helper class to test ColumXXXX and MatrixXXX classes,
    the one that stores files in their x.raw_content field.

    Handles the file storage.
    """
    try:
        c = clss(**kwargs)
        base_name = os.path.basename(file_path)
        # with open(file_path, 'r') as f:
        # `rb` for read bytes. Necessary for azure storage.
        with open(file_path, 'rb') as f:
            c.raw_content.save(base_name, f)
            c.save()
        return c
    except Exception as e:
        log.error("Problem creating from file: clss=%r, path=%s\n%e", clss, file_path, e)
        raise e


def chalearn_path(path, suffix, any_prefix=False):
    if any_prefix:
        l = fs.ls(path, '*%s' % suffix, glob=True)

        if len(l) != 1:
            raise FileNotFoundError("""Expected a match for: %s/*%s, got no/multiple results: %s"""
                                    % (path, suffix, l))
        return l[0]
    else:
        name = path.split('/')[-1]
        p = os.path.join(path, '%s%s' % (name, suffix))
        return p


def load_chalearn(path, suffix, clss=MatrixModel, any_prefix=False, **kwargs):
    return create_with_file(clss,
                            chalearn_path(path, suffix, any_prefix=any_prefix),
                            **kwargs)


class TaskModel(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True)
    is_public = models.BooleanField(default=False, null=False)
    is_ready = models.BooleanField(default=False, null=False)
    name = models.CharField(max_length=256, null=False)
    dataset = models.ForeignKey(DatasetModel, null=True, on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)

    train_ratio = models.FloatField(null=True,
                                    default=85,
                                    verbose_name='Ratio for train data (percents)')
    valid_ratio = models.FloatField(null=True,
                                    default=5,
                                    verbose_name='Ratio for valid data (percents)')
    test_ratio = models.FloatField(null=True,
                                   default=10,
                                   verbose_name='Ratio for test data (percents)')

    # TODO(laurent): This pattern of having a single model reference by many fields
    # is not viable. We should define a model instance per use case (training, etc).
    # Similar to what we do for the columnar storage model.
    input_train = OneToOneField(MatrixModel, null=True, related_name='model_trained')
    target_train = OneToOneField(MatrixModel, null=True, related_name='model_trained_target')

    input_test = OneToOneField(MatrixModel, null=True, related_name='model_tested')
    target_test = OneToOneField(MatrixModel, null=True, related_name='model_tested_target')

    input_valid = OneToOneField(MatrixModel, null=True, related_name='model_validated')
    target_valid = OneToOneField(MatrixModel, null=True, related_name='model_validated_target')

    def __str__(self):
        return "<%s: \"%s\"; id=%s; ready=%s>" % (type(self).__name__, self.name, self.id, self.is_ready)

    @property
    def has_content(self):
        return not None in [
            self.input_train, self.target_train,
            self.input_test,
            # self.target_test,
            #  TODO: we skip this case because in current testing cases we don't have the data.
            self.input_valid, self.target_valid
        ]

    @property
    def template_mapping(self):
        return {}

    @property
    def template_doc(self):
        return {}

    def clean(self):
        super().clean()

        if self.dataset is not None:
            self.name = self.dataset.name

        if self.test_ratio is not None and self.train_ratio is not None and self.valid_ratio is not None:
            s = self.test_ratio + self.train_ratio + self.valid_ratio

            if round(s,10) != 100:
                raise ValidationError('invalid ratios: sum is not 100%%: %s' % s)

        # TODO(laurent): there are some subtleties on the validation
        # regarding nested fields. We also do not need to duplicate
        # the metadata for the columns between each input.

        self.is_ready = self.is_ready or (self.input_test is not None and
                         self.target_train is not None and
                         self.input_test is not None and
                         self.input_valid is not None and
                         self.target_valid is not None)

    def save(self, *args, **kwargs):
        self.clean()  # Force clean on save.
        super().save(*args, **kwargs)

    def update_from_chalearn(self, path):
        loaded = self.load_from_chalearn(path)
        for k, v in loaded.items():
            setattr(self, k, v)
        self.save()

    @classmethod
    def load_from_chalearn(cls, path):
        train = load_chalearn(path, '_train.data')
        train_target = load_chalearn(path, '_train.solution')

        test = load_chalearn(path, '_test.data')
        test_target = load_chalearn(path, '_test.solution')

        valid = load_chalearn(path, '_valid.data')
        valid_target = load_chalearn(path, '_valid.solution')

        train_count = train.rows.count
        valid_count = valid.rows.count
        test_count = test.rows.count
        total = train_count + valid_count + test_count

        return dict(input_train=train, target_train=train_target,
                    input_test=test, target_test=test_target,
                    input_valid=valid, target_valid=valid_target,
                    train_ratio=train_count*100/total,
                    valid_ratio=valid_count*100/total,
                    test_ratio=100-(train_count*100/total)
                               -(valid_count*100/total),
                    is_ready=True)

    @classmethod
    def from_chalearn(cls, dataset, path, name):
        return cls.objects.create(
            dataset=dataset,
            owner=None, is_public=True, name=name,
            **cls.load_from_chalearn(path)
        )

    def deep_copy(self):
        self.id = None

        self.input_train = self.input_train.deep_copy() if self.input_train is not None else None
        self.target_train = self.target_train.deep_copy() if self.target_train is not None else None
        self.input_test = self.input_test.deep_copy() if self.input_test is not None else None
        self.target_test = self.target_test.deep_copy() if self.target_test is not None else None
        self.input_valid = self.input_valid.deep_copy() if self.input_valid is not None else None
        self.target_valid = self.target_valid.deep_copy() if self.target_valid is not None else None

        self.save()
        return self

    def delete(self):
        delete_all([self.input_train, self.target_train, self.input_test,
                    self.target_test, self.input_valid, self.target_valid])
        super().delete()


class MetricModel(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=256, null=False)
    description = models.TextField(null=False, default="", blank=True)
    code = models.TextField(null=False, default="", blank=True)

    is_default = models.BooleanField(default=False, null=False)
    is_public = models.BooleanField(default=False, null=False)
    is_ready = models.BooleanField(default=False, null=False)

    classification = models.BooleanField(default=False, null=False)
    regression = models.BooleanField(default=False, null=False)

    def __str__(self):
        return "<%s: \"%s\"; id=%s>" % (type(self).__name__, self.name, self.id)

    @property
    def template_mapping(self):
        return {'metric_name': self.name}

    @property
    def template_doc(self):
        return {'metric_name': ''}

    def delete(self):
        if not self.is_default and not self.is_public:
            super().delete()


DEV_PHASE_DESC = """Development phase: create models and submit them or directly submit results on validation and/or test data; feed-back are provided on the validation set only."""
FINAL_PHASE_DESC = """Final phase: submissions from the previous phase are automatically cloned and used to compute the final score. The results on the test set will be revealed when the organizers make them available."""


class ProtocolModel(models.Model):
    is_ready = models.BooleanField(default=False, null=False)

    dev_phase_label = models.CharField(max_length=128, default="Development", verbose_name="Label")
    dev_phase_description = models.TextField(max_length=2048, verbose_name="Description",
                                             default=DEV_PHASE_DESC)
    dev_start_date = models.DateTimeField(null=True, default=None, blank=True,
                                          verbose_name='Start date')

    final_phase_label = models.CharField(max_length=128, default="Final", verbose_name="Label")
    final_phase_description = models.TextField(max_length=2048, verbose_name="Description",
                                               default=FINAL_PHASE_DESC)
    final_start_date = models.DateTimeField(null=True, default=None, blank=True,
                                            verbose_name='Start date')

    max_submissions_per_day = models.PositiveIntegerField(null=True, default=5, blank=True)
    max_submissions = models.PositiveIntegerField(null=True, default=10, blank=True)

    def __str__(self):
        return "<%s: id=%s; ready=%s>" % (type(self).__name__, self.id, self.is_ready)

    def clean(self):
        super().clean()
        self.is_ready = self.dev_start_date is not None and self.final_start_date is not None

    def save(self, *args, **kwargs):
        self.clean()  # Force clean on save
        self.challenge.updated_at = datetime.now()
        super().save(*args, **kwargs)

    @property
    def template_mapping(self):
        return {'protocol_max_submissions_per_day': self.max_submissions_per_day,
                'protocol_max_submissions': self.max_submissions,
                'protocol_dev_start_date': self.dev_start_date,
                'protocol_final_start_date': self.final_start_date}

    @property
    def template_doc(self):
        return {'protocol_max_submissions_per_day': '',
                'protocol_max_submissions': ''}


class DocumentationModel(models.Model):
    default_pages = docs.DEFAULT_PAGES
    is_ready = models.BooleanField(default=True, null=False)

    def __str__(self):
        return "<%s: id=%s; ready=%s>" % (type(self).__name__, self.id, self.is_ready)

    @property
    def pages(self):
        return DocumentationPageModel.objects.filter(documentation=self)

    def save(self, *args, **kwargs):
        self.is_ready = all(page.is_rendered for page in self.pages)

        try:
            self.challenge.updated_at = datetime.now()
        except ChallengeModel.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    @classmethod
    def create(cls, render_for=None):
        c = cls.objects.create()

        if render_for:
            mapping = challenge_to_mappings(render_for)
        else:
            mapping = None

        for i, p in enumerate(cls.default_pages):
            pm = DocumentationPageModel.create(doc=c,
                                               pos=i,
                                               name=p['name'],
                                               content=p['content'])
            if mapping:
                pm.render(mapping)

        return c

    @property
    def template_mapping(self):
        return {}

    @property
    def template_doc(self):
        return {}


def challenge_to_mappings(challenge):
    c = challenge
    ls = [x for x in (c, c.dataset, c.task, c.metric, c.protocol, c.documentation, c.baseline)
          if x is not None]

    mappings = {}
    for x in ls:
        mappings.update(x.template_mapping)
    return mappings


def challenge_to_mappings_doc(challenge):
    c = challenge
    ls = [x for x in (c, c.dataset, c.task, c.metric, c.protocol, c.documentation)
          if x is not None]

    mappings = {}
    for x in ls:
        mappings.update(x.template_doc)
    return mappings


class DocumentationPageModel(models.Model):
    name = models.CharField(max_length=80, validators=[validate_slug])
    pos = models.IntegerField()

    content = HTMLField()
    rendered = HTMLField(null=True, blank=True)

    documentation = models.ForeignKey(DocumentationModel, on_delete=models.CASCADE)

    def __str__(self):
        return "<%s: \"%s\"; pos=%s>" % (type(self).__name__,
                                                  self.name, self.pos)

    def render(self, mapping_values):
        template = string.Template(self.content)
        self.rendered = template.safe_substitute(mapping_values)
        self.save()

    def save(self, **kwargs):
        self.full_clean()
        super().save(**kwargs)

    @property
    def template_doc(self):
        return self.documentation.challenge.first().template_doc

    @property
    def displayed(self):
        return self.rendered if self.is_rendered else self.content

    @property
    def is_rendered(self):
        return self.rendered is not None

    @classmethod
    def create(cls, doc, name, content, pos=0):
        return cls.objects.create(documentation=doc,
                                  pos=pos,
                                  name=name,
                                  content=content)

    class Meta:
        ordering = ['pos']


class BaselineModel(models.Model):
    submission = models.FileField(upload_to=save_to_baseline,
                                  verbose_name='baseline submission',
                                  blank=True, null=True)

    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            this = BaselineModel.objects.get(id=self.id)
            if this.submission != self.submission:
                this.submission.delete(save=False)
        except:
            pass  # when new baseline then we do nothing, normal case
        super(BaselineModel, self).save(*args, **kwargs)

    def delete(self):
        try:
            self.submission.delete(save=False)
        except:
            pass
        super().delete()

    def __str__(self):
        return "<%s: id=%s>" % (type(self).__name__, self.id)

    @property
    def absolute_uri(self):
        if self.submission:
            url = self.submission.url
            url = build_absolute_uri(url)
        else:
            url = "UNDEFINED"

        return url

    @property
    def is_ready(self):
        return bool(self.submission)

    @property
    def template_mapping(self):
        return {'baseline_submission_url': self.absolute_uri}

    @property
    def template_doc(self):
        return {'baseline_submission_url': "URL to download the baseline submission zip."}


class ChallengeModel(models.Model):
    title = models.CharField(max_length=60)
    organization_name = models.CharField(max_length=80, blank=True)
    description = models.TextField(max_length=255, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to=save_to_logo)

    origin_group = models.ForeignKey('group.GroupModel', null=True, blank=True, on_delete=models.SET_NULL)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    build_at = models.DateTimeField(default=timezone.now)

    dataset = models.ForeignKey(DatasetModel, null=True, blank=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(TaskModel, null=True, blank=True, on_delete=models.SET_NULL)
    metric = models.ForeignKey(MetricModel, null=True, blank=True, on_delete=models.SET_NULL)
    protocol = models.ForeignKey(ProtocolModel, null=True, blank=True,
                                 related_name='challenge', on_delete=models.SET_NULL)
    baseline = models.OneToOneField(BaselineModel, null=True, blank=True,
                                    related_name='challenge', on_delete=models.SET_NULL)
    documentation = models.OneToOneField(DocumentationModel, null=True,
                                         blank=True, related_name='challenge', on_delete=models.SET_NULL)

    def __str__(self):
        return "<%s: \"%s\"; id=%s>" % (type(self).__name__,
                                                 self.title,
                                                 self.id)

    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            this = ChallengeModel.objects.get(id=self.id)
            if this.logo != self.logo:
                this.logo.delete(save=False)
        except:
            pass  # when new photo then we do nothing, normal case
        super(ChallengeModel, self).save(*args, **kwargs)

    @property
    def is_ready(self):
        return len(self.missings) == 0

    def create_initial_task(self):
        self.task = TaskModel.objects.create(
            owner=self.created_by,
            is_public=False,
            name='task for %s' % self.dataset.name,
            dataset=self.dataset
        )
        self.save()

    def generate_default_phases(self):
        self.append_phase('development')
        self.append_phase('final')

    def append_phase(self, name):
        p = PhaseModel.create(name=name, challenge=self,
                              position=self.phases.count())
        return p

    @property
    def missings(self):
        missing = []

        required = ['dataset', 'task', 'metric', 'protocol', 'baseline', 'documentation']
        for x in required:
            v = getattr(self, x)

            if v is None:
                missing.append(x)
            else:
                if not v.is_ready:
                    missing.append(x)

        return missing

    @property
    def template_mapping(self):
        return {'challenge_title': self.title,
                'challenge_organization_name': self.organization_name,
                'challenge_description': self.description}

    @property
    def template_doc(self):
        return {'challenge_title': "",
                'challenge_organization_name': "",
                'challenge_description': ""}

    def get_absolute_url(self):
        return reverse('wizard:challenge', kwargs={'pk': self.pk})

    @classmethod
    def get(cls, pk):
        return cls.objects.get(pk=pk)

    def delete(self):
        delete_all([self.task, self.metric, self.protocol,
                    self.baseline, self.documentation])

        try:
            self.logo.delete(save=False)
        except:
            pass

        super().delete()


class PhaseModel(models.Model):
    name = models.CharField(max_length=60)
    challenge = models.ForeignKey(ChallengeModel, related_name='phases')

    def __str__(self):
        return "<%s: \"%s\"; chal=%s>" % (type(self).__name__,
                                                 self.name,
                                                 self.challenge)

    @classmethod
    def create(cls, name, challenge, position):
        return cls.objects.create(name=name, challenge=challenge)
