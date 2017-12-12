import os
from django.core.exceptions import ValidationError


def validate_file(ext, temp_file):
    file_ext =  os.path.splitext(temp_file.name)[1]
    if not file_ext.lower() == ext:
        raise ValidationError('Expected a file extension of {0}, received {1} instead.'.format(ext, file_ext))


def validate_py_file(temp_file):
    validate_file('.py', temp_file)


def validate_zip_file(temp_file):
    validate_file('.zip', temp_file)


def validate_image_file(temp_file):
    validate_file('.zip', temp_file)