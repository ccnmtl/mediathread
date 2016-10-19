from django.db import models
from django.contrib.auth.models import User
from courseaffils.models import Course
from mediathread.djangosherd.models import SherdNote


class JuxtaposeAsset(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    title = models.TextField()
    spine = models.ForeignKey(SherdNote, blank=True, null=True)


class JuxtaposeMediaElement(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    juxtaposition = models.ForeignKey(JuxtaposeAsset)
    start_time = models.DecimalField(
        max_digits=12, decimal_places=5)
    end_time = models.DecimalField(
        max_digits=12, decimal_places=5)
    media = models.ForeignKey(SherdNote)


class JuxtaposeTextElement(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    juxtaposition = models.ForeignKey(JuxtaposeAsset)
    start_time = models.DecimalField(
        max_digits=12, decimal_places=5)
    end_time = models.DecimalField(
        max_digits=12, decimal_places=5)
    text = models.TextField()
