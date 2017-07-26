from django.contrib import admin

from .models import (DatasetModel, TaskModel, MetricModel, ChallengeModel,
                     DocumentationModel, DocumentationPageModel, MatrixModel,
                     AxisDescriptionModel, BaselineModel)

admin.site.register(AxisDescriptionModel)
admin.site.register(BaselineModel)
admin.site.register(ChallengeModel)
admin.site.register(DatasetModel)
admin.site.register(DocumentationModel)
admin.site.register(DocumentationPageModel)
admin.site.register(MatrixModel)
admin.site.register(MetricModel)
admin.site.register(TaskModel)
