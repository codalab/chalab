from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class ChallengeModel(models.Model):
    title = models.CharField(max_length=60)
    organization_name = models.CharField(max_length=80)
    description = models.TextField(max_length=255)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('wizard:challenge', kwargs={'pk': self.pk})


class ChallengeDataModel(models.Model):
    challenge = models.ForeignKey(ChallengeModel, on_delete=models.CASCADE, related_name='data')
    name = models.CharField(max_length=80, default="")

    K_CHALEARN_ADULT = 'chalearn/adult'
    K_CHALEARN_ALEXIS = 'chalearn/alexis'
    K_CHALEARN_CHRISTINE = 'chalearn/christine'
    K_CHALEARN_DILBERT = 'chalearn/dilbert'
    K_CHALEARN_DOROTHEA = 'chalearn/dorothea'
    K_CHALEARN_FABERT = 'chalearn/fabert'
    K_CHALEARN_JANNIS = 'chalearn/jannis'
    K_CHALEARN_MADELINE = 'chalearn/madeline'

    DATA_SET_KIND = [
        (K_CHALEARN_ADULT, 'Chalearn: Adult'),
        (K_CHALEARN_ALEXIS, 'Chalearn: Alexis'),
        (K_CHALEARN_CHRISTINE, 'Chalearn: Christine'),
        (K_CHALEARN_DILBERT, 'Chalearn: Dilbert'),
        (K_CHALEARN_DOROTHEA, 'Chalearn: Dorothea'),
        (K_CHALEARN_FABERT, 'Chalearn: Fabert'),
        (K_CHALEARN_JANNIS, 'Chalearn: Jannis'),
        (K_CHALEARN_MADELINE, 'Chalearn: Madeline'),
    ]

    kind = models.CharField(choices=DATA_SET_KIND, max_length=30, default=K_CHALEARN_ADULT)

    def get_absolute_url(self):
        return reverse('wizard:data', kwargs={'pk': self.challenge.pk})
