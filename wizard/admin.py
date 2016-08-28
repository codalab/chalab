from django.contrib import admin

from .models import DatasetModel, TaskModel

admin.site.register(DatasetModel)
admin.site.register(TaskModel)
