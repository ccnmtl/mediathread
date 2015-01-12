from django.conf import settings
from django.contrib.auth.models import Group


class CourseGroupMapper(object):
    """ See if the user is part of any existing course. If so, add them
        as a member """

    def map(self, user, affils):
        # we also make a "pseudo" affil group ALL_CU
        # that contains *anyone* who's logged in through WIND
        affils.append("ALL_CU")

        # by default, WIND affils include a group named for
        # the uni for each user. This is not usually desirable
        # so we strip it out, but there's a setting that lets
        # you turn it back on.
        remove_uni = True
        if hasattr(settings, 'WIND_AFFIL_GROUP_INCLUDE_UNI_GROUP'):
            if settings.WIND_AFFIL_GROUP_INCLUDE_UNI_GROUP is True:
                remove_uni = False

        for affil in affils:
            if remove_uni and (affil == user.username):
                continue
            try:
                group = Group.objects.get(name=affil)
                user.groups.add(group)
                user.save()
            except Group.DoesNotExist:
                pass
