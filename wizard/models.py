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

    def get_absolute_url(self):
        return reverse('wizard:data', kwargs={'cpk': self.challenge.pk, 'pk': self.pk})
