from django.forms import ModelForm, DateInput

from .models import ProtocolModel


class ProtocolForm(ModelForm):
    class Meta:
        model = ProtocolModel
        fields = ['end_date', 'allow_reuse', 'publicly_available',
                  'has_registration', 'ranked_submissions',
                  'max_submissions_per_day', 'max_submissions']
        widgets = {
            'end_date': DateInput(attrs={'class': 'date-picker'})
        }
