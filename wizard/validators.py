import os
from django.core.exceptions import ValidationError


def validate_file(ext_list, temp_file):
    file_ext = os.path.splitext(temp_file.name)[1]
    if file_ext.lower() not in ext_list:
        raise ValidationError('Expected one of these file types {0}; Received {1} instead.'.format(ext_list, file_ext))


def validate_zip_file(temp_file):
    validate_file(['.zip'], temp_file)


def validate_image_file(temp_file):
    validate_file(['.png', '.jpg', '.jpeg', '.gif'], temp_file)
