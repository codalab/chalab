from django.forms import ModelForm, DateInput, FileField

from .models import ProtocolModel, DatasetModel


class ProtocolForm(ModelForm):
    class Meta:
        model = ProtocolModel
        fields = ['dev_start_date', 'dev_end_date',
                  'final_start_date', 'final_end_date',
                  'allow_reuse', 'publicly_available',
                  'has_registration', 'ranked_submissions',
                  'max_submissions_per_day', 'max_submissions']
        widgets = {
            'dev_start_date': DateInput(attrs={'class': 'date-picker'}),
            'dev_end_date': DateInput(attrs={'class': 'date-picker'}),
            'final_start_date': DateInput(attrs={'class': 'date-picker'}),
            'final_end_date': DateInput(attrs={'class': 'date-picker'})
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
