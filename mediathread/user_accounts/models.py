from django.db import models
from django.contrib.auth.models import User


class RegistrationModel(models.Model):
    HEAR_CHOICES = (
        ('CO', 'Conference'),
        ('WS', 'Web Search'),
        ('WM', 'World of mouth'),
        ('OT', 'Other')
    )
    POSITION_CHOICES = (
        ('PF', 'Professor'),
        ('ST', 'Student'),
        ('SA', 'Administrator'),
        ('IT', 'Instructional Technologist'),
        ('RD', 'Developer'),
        ('OT', 'Other')
    )

    user = models.OneToOneField(User, editable=True, null=True, related_name="registration_model")
    organization = models.ForeignKey('OrganizationModel')
    hear_mediathread_from = models.CharField("How did you hear about Mediathread?",
                                             max_length=2, choices=HEAR_CHOICES)
    position_title = models.CharField("Which best describes you?", max_length=2, choices=POSITION_CHOICES)
    subscribe_to_newsletter = models.BooleanField("Yes, subscribe me to the Mediathread newsletter.")


class OrganizationModel(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
