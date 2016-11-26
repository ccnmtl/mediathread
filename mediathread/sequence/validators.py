from rest_framework.serializers import ValidationError


def prevent_overlap(value):
    """Validate that the given list doesn't have any overlapping objects.

    Expects a list of objects that each have a start_time and end_time.
    """
    for i in range(len(value) - 1):
        a = value[i]
        b = value[i + 1]
        overlap = a.get('start_time') <= b.get('end_time') and \
            b.get('start_time') <= a.get('end_time')
        if overlap:
            raise ValidationError('Elements can\'t overlap.')


def valid_start_end_times(value):
    """Validate that each object's end time is greater than its start time.

    Expects a list of objects that each have a start_time and end_time.
    """
    for e in value:
        if e.get('end_time') <= e.get('start_time'):
            raise ValidationError(
                'Each element\'s end time must be greater than its '
                'start time.')
