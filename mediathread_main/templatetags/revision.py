from django import template
from django.conf import settings
from release_id import LAST_GIT_HEAD

register = template.Library()


@register.simple_tag
def revision():
    if settings.DEBUG:
        return 1  # import random; str(random.randint(0,320000)) # 1
    else:
        return LAST_GIT_HEAD
