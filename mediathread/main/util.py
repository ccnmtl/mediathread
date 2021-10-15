from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email
from django.template import loader
import requests
from requests.exceptions import SSLError
from sentry_sdk import capture_exception


def send_template_email(subject, template_name, params, recipient):
    validate_email(recipient)

    template = loader.get_template(template_name)
    message = template.render(params)
    send_mail(subject, message, settings.SERVER_EMAIL, [recipient])


def send_course_invitation_email(request, invite):
    invite_template = 'dashboard/email_invite_user.txt'

    subject = "Mediathread Course Invitation: {}".format(
        request.course.title)

    ctx = {
        'course': request.course,
        'domain': get_current_site(request).domain,
        'invite': invite,
        'inviter': user_display_name(request.user)
    }
    send_template_email(subject, invite_template, ctx, invite.email)


def user_display_name(user):
    return user.get_full_name() or user.username


def user_display_name_last_first(user):
    if user is None or \
       (hasattr(user, 'is_anonymous') and user.is_anonymous):
        return 'Anonymous'

    if user.first_name and user.last_name:
        return '{}, {}'.format(
            user.last_name, user.first_name)

    return user.username


def make_pmt_item(data):
    """Make a PMT item containing the given data.

    This function requires TASK_ASSIGNMENT_DESTINATION to be set.
    """
    TASK_ASSIGNMENT_DESTINATION = getattr(
        settings, 'TASK_ASSIGNMENT_DESTINATION', None)

    if not TASK_ASSIGNMENT_DESTINATION:
        raise ImproperlyConfigured

    try:
        return requests.post(TASK_ASSIGNMENT_DESTINATION, data=data)
    except SSLError as e:
        capture_exception(e)
