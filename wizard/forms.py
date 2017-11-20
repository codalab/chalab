from django.forms import ModelForm, FileField, DateTimeInput, Textarea, TextInput, BooleanField

from .models import ProtocolModel, DatasetModel, TaskModel

from django.utils import timezone


def naive_suffix(x):
    x.label = "%s*" % (x.label,)
    return x


class TaskModelForm(ModelForm):
    class Meta:
        model = TaskModel
        fields = [
            'train_ratio',
            'valid_ratio',
            'test_ratio',
        ]


class ProtocolForm(ModelForm):
    def phase_1(self):
        return [naive_suffix(x) for x in self
                if x.name.startswith('dev')]

    def phase_2(self):
        return [naive_suffix(x) for x in self
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
            'dev_phase_description': Textarea(attrs={'rows': 3, 'style':'resize:none;'}),
            'final_phase_description': Textarea(attrs={'rows': 3, 'style':'resize:none;'}),

            'dev_start_date': DateTimeInput(attrs={'class': 'datetime-picker'}),
            'dev_end_date': DateTimeInput(attrs={'class': 'datetime-picker'}),
            'final_start_date': DateTimeInput(attrs={'class': 'datetime-picker'}),
            'final_end_date': DateTimeInput(attrs={'class': 'datetime-picker'})
        }


class DataUpdateForm(ModelForm):
    class Meta:
        model = DatasetModel
        # fields = ['display_name', 'name', 'raw_zip_name', 'description', 'show_date_on_display']
        fields = ['description']
        labels = {
            'description': 'Description or Label ( Leave blank for date last modified )',
            # 'show_date_on_display': 'Use Date Last Modified For Description?'
        }
        widgets = {
            'description': TextInput(
                attrs={
                    'placeholder': timezone.now().date(),
                    'maxlength': '20',
                       }
            ),
        }


class DataUpdateAndUploadForm(DataUpdateForm):
    automl_upload = FileField(required=False)

    class Meta(DataUpdateForm.Meta):
        fields = DataUpdateForm.Meta.fields + [
            'automl_upload'
        ]

    def do_hide(self):
        self.fields['automl_upload'] = HiddenField()
