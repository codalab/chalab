from django.forms import ModelForm, FileField, DateTimeInput

from .models import ProtocolModel, DatasetModel


class ProtocolForm(ModelForm):
    class Meta:
        model = ProtocolModel
        fields = [
            'dev_phase_description',
            'dev_start_date', 'dev_end_date',
            'dev_execution_time_limit',

            'final_phase_description',
            'final_start_date', 'final_end_date',
            'final_execution_time_limit',

            'max_submissions_per_day', 'max_submissions']
        widgets = {
            'dev_start_date': DateTimeInput(attrs={'class': 'datetime-picker'}),
            'dev_end_date': DateTimeInput(attrs={'class': 'datetime-picker'}),
            'final_start_date': DateTimeInput(attrs={'class': 'datetime-picker'}),
            'final_end_date': DateTimeInput(attrs={'class': 'datetime-picker'})
        }


class DataUpdateForm(ModelForm):
    class Meta:
        model = DatasetModel
        fields = ['name']


class DataUpdateAndUploadForm(DataUpdateForm):
    automl_upload = FileField(required=False)

    class Meta(DataUpdateForm.Meta):
        fields = DataUpdateForm.Meta.fields + [
            'automl_upload'
        ]
