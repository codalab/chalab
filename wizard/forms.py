from django.forms import ModelForm, FileField, DateTimeInput

from .models import ProtocolModel, DatasetModel


class ProtocolForm(ModelForm):
    def phase_1(self):
        return [x for x in self
                if x.name.startswith('dev')]

    def phase_2(self):
        return [x for x in self
                if x.name.startswith('final')]

    class Meta:
        model = ProtocolModel
        fields = [
            'dev_phase_label',
            'dev_phase_description',
            'dev_start_date',

            'final_phase_label',
            'final_phase_description',
            'final_start_date'
        ]
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
