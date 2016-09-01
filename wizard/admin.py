from django.contrib import admin

from .models import DatasetModel, TaskModel, MetricModel, ChallengeModel

admin.site.register(DatasetModel)
admin.site.register(TaskModel)
admin.site.register(MetricModel)
admin.site.register(ChallengeModel)
