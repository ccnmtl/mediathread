import uuid

from courseaffils.models import Course
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import UUIDField
from registration.signals import user_registered, user_activated

from mediathread.main.course_details import get_guest_sandbox


class UserSetting(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    @classmethod
    def get_setting(cls, user, setting_id, default_value):
        try:
            user_setting = UserSetting.objects.get(user=user, name=setting_id)

            if (user_setting.value == 'True' or
                    user_setting.value == 'true'):
                return True
            elif (user_setting.value == 'False' or
                    user_setting.value == 'false'):
                return False
            else:
                return user_setting.value
        except:
            return default_value

    @classmethod
    def set_setting(cls, user, setting_id, value):
        try:
            user_setting = UserSetting.objects.get(user=user, name=setting_id)
            user_setting.value = str(value)
            user_setting.save()
        except:
            UserSetting.objects.create(user=user, name=setting_id, value=value)


class UserProfile(models.Model):
    '''UserProfile adds extra information to a user,
    and associates the user with a group, school,
    and country.'''
    user = models.OneToOneField(User, related_name='profile')
    title = models.CharField(max_length=256, null=True, blank=True)
    institution = models.TextField()
    referred_by = models.TextField()
    user_story = models.TextField(null=True, blank=True)
    self_registered = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username


def user_registered_callback(sender, user, request, **kwargs):
    user.first_name = request.POST['first_name'].strip()
    user.last_name = request.POST['last_name'].strip()
    user.save()

    UserProfile.objects.create(user=user,
                               self_registered=True,
                               title=request.POST['title'].strip(),
                               institution=request.POST['institution'].strip(),
                               referred_by=request.POST['referred_by'],
                               user_story=request.POST['user_story'])


def user_activated_callback(sender, user, request, **kwargs):
    # add this user to the guest sandbox by default
    sandbox = get_guest_sandbox()
    sandbox.group.user_set.add(user)


user_registered.connect(user_registered_callback)
user_activated.connect(user_activated_callback)


class CourseInvitation(models.Model):
    email = models.EmailField()
    course = models.ForeignKey(Course)
    uuid = UUIDField(default=uuid.uuid4, editable=False)

    activated_at = models.DateTimeField(null=True)

    invited_by = models.ForeignKey(User)
    invited_at = models.DateTimeField(auto_now_add=True)

    def activated(self):
        return self.activated_at is not None


class Affil(models.Model):
    """Model for storing activatable affiliations.

    Faculty use this to 'activate' it into a Group/Course.
    """
    class Meta:
        unique_together = ('name', 'user')

    activated = models.BooleanField(default=False)
    name = models.TextField()
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    @property
    def courseworks_name(self):
        """Returns the Courseworks formatted name.

        e.g.: CUcourse_NURSN6610_001_2008_2

        If no mapper is configured, returns None.
        """
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER') and \
           settings.COURSEAFFILS_COURSESTRING_MAPPER is not None:
            affil_dict = settings.COURSEAFFILS_COURSESTRING_MAPPER.to_dict(
                self.name)
            return 'CUcourse_{}{}{}_{}_{}_{}'.format(
                affil_dict['dept'].upper(),
                affil_dict['letter'],
                affil_dict['number'],
                affil_dict['section'],
                affil_dict['year'],
                affil_dict['term'])
        return None

    @property
    def coursedirectory_name(self):
        """Returns the Course Directory formatted name.

        e.g.: 20082NURS6610N001

        If no mapper is configured, returns None.
        """
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER') and \
           settings.COURSEAFFILS_COURSESTRING_MAPPER is not None:
            affil_dict = settings.COURSEAFFILS_COURSESTRING_MAPPER.to_dict(
                self.name)
            return '{}{}{}{}{}{}'.format(
                affil_dict['year'],
                affil_dict['term'],
                affil_dict['dept'].upper(),
                affil_dict['number'],
                affil_dict['letter'].upper(),
                affil_dict['section'])
        return None
