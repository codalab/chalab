from django.contrib import admin

from .models import (DatasetModel, TaskModel, MetricModel, ChallengeModel,
                     DocumentationModel, DocumentationPageModel, MatrixModel,
                     AxisDescriptionModel)

admin.site.register(AxisDescriptionModel)
admin.site.register(MatrixModel)
admin.site.register(DatasetModel)
admin.site.register(TaskModel)
admin.site.register(MetricModel)
admin.site.register(ChallengeModel)
admin.site.register(DocumentationModel)
admin.site.register(DocumentationPageModel)
