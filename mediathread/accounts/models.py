from django.db import models

# Create your models here.

class RegistrationModel(models.Model):
    HEAR_CHOICES = (
        ('GA', 'Google Ads'),
        ('MF', 'My Friends'),
        ('MT', 'My Teacher'),
        ('MC', 'My Cat')
        )
    
    email = models.EmailField()
    password = models.CharField(max_length=16)
    fullname = models.CharField(max_length=30)
    organization = models.CharField(max_length=50)
    course_title = models.CharField(max_length=50)
    hear_mediathread_from = models.CharField(max_length=2, choices=HEAR_CHOICES)
    subscribe_to_newsletter = models.BooleanField()
    
