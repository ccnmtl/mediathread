from django.db import models
from django.contrib.auth.models import User


class RegistrationModel(models.Model):
    HEAR_CHOICES = (
        ('conference', 'Conference'),
        ('web_search', 'Web Search'),
        ('word_of_mouth', 'Word of mouth'),
        ('other', 'Other')
    )
    POSITION_CHOICES = (
        ('professor', 'Professor'),
        ('student', 'Student'),
        ('administrator', 'Administrator'),
        ('instructional_technologist', 'Instructional Technologist'),
        ('developer', 'Developer'),
        ('other', 'Other')
    )

    user = models.OneToOneField(User, editable=True, null=True, related_name="registration_model")
    organization = models.ForeignKey('OrganizationModel')
    hear_mediathread_from = models.CharField("How did you hear about Mediathread?",
                                             max_length=30, choices=HEAR_CHOICES)
    position_title = models.CharField("Which best describes you?", max_length=30, choices=POSITION_CHOICES)
    subscribe_to_newsletter = models.BooleanField("Yes, subscribe me to the Mediathread newsletter.")


class OrganizationModel(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
