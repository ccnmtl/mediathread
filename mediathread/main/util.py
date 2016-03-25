from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.template.context import Context


def send_template_email(subject, template_name, params, recipient):
    template = loader.get_template(template_name)
    message = template.render(Context(params))
    send_mail(subject, message, settings.SERVER_EMAIL, [recipient])


def user_display_name(user):
    return user.get_full_name() or user.username
