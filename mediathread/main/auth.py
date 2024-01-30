from django.conf import settings
from django.contrib.auth.models import Group
from django.utils import timezone
from courseaffils.models import Affil


class CourseGroupMapper(object):
    """
    See if the user is part of any existing course. If so, add them
    as a member.
    """

    @staticmethod
    def create_activatable_affil(
            user: object, course_string: str, year: int) -> Affil:
        """Create an Affil for the affil/user.

        The required conditions are:
        - The user has 'faculty' status for this affil
        - The affil has a recent or future date.

        Returns the Affil if created, otherwise returns None.
        """
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
            d = settings.COURSEAFFILS_COURSESTRING_MAPPER.to_dict(
                course_string)
        else:
            return None

        try:
            conditions = user is not None and \
                         user.is_authenticated and \
                         d is not None and \
                         d['member'] == 'fc' and \
                         year is not None and \
                         year <= int(d['year'])
        except KeyError:
            return None

        if conditions:
            return Affil.objects.get_or_create(
                name=course_string, user=user)[0]

        return None

    @staticmethod
    def map(user: object, affils: list):
        # we also make a "pseudo" affil group ALL_CU
        # that contains *anyone* who's logged in through CAS
        affils.append('ALL_CU')

        # by default, CAS affils include a group named for
        # the uni for each user. This is not usually desirable
        # so we strip it out, but there's a setting that lets
        # you turn it back on.
        remove_uni = True
        if hasattr(settings, 'CAS_AFFIL_GROUP_INCLUDE_UNI_GROUP'):
            if settings.CAS_AFFIL_GROUP_INCLUDE_UNI_GROUP is True:
                remove_uni = False

        year = timezone.now().year

        for course_string in affils:
            if remove_uni and (course_string == user.username):
                continue
            try:
                group = Group.objects.get(name=course_string)
                user.groups.add(group)
                user.save()
            except Group.DoesNotExist:
                CourseGroupMapper.create_activatable_affil(
                    user, course_string, year)
