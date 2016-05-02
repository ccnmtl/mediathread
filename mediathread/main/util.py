from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import loader
from django.template.context import Context


def send_template_email(subject, template_name, params, recipient):
    template = loader.get_template(template_name)
    message = template.render(Context(params))
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
