from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class ProfileModel(models.Model):
    EX_NOVICE = "NO"
    EX_FAMILIAR = "FA"
    EX_EXPERT = "EX"

    EXPERTISE_CHOICES = (
        (EX_NOVICE, "Novice"),
        (EX_FAMILIAR, "Familiar"),
        (EX_EXPERT, "Expert")
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    first_name = models.CharField(max_length=80, null=True)
    last_name = models.CharField(max_length=80, null=True)

    affiliation = models.CharField(max_length=80, null=True, blank=True)
    expertise = models.CharField(max_length=2, choices=EXPERTISE_CHOICES, null=True)

    def get_absolute_url(self):
        return reverse('user:profile')
