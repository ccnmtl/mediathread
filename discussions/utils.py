from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType
from courseaffils.models import Course

ThreadedComment = get_model('threadedcomments', 'threadedcomment')
Collaboration = get_model('structuredcollaboration', 'collaboration')


def get_discussions(arbitrary_object):
    coll = ContentType.objects.get_for_model(Collaboration)
    discussions = []
    comments = ThreadedComment.objects.filter(parent=None, content_type=coll)

    for d in comments:
        if d.content_object and d.content_object._parent_id and \
                arbitrary_object == d.content_object._parent.content_object:
            discussions.append(d)
    return discussions


def get_course_discussions(course):

    content_type = ContentType.objects.get_for_model(Course)
    parent = Collaboration.objects.get(object_pk=course.id,
                                       content_type=content_type)

    content_type = ContentType.objects.get_for_model(ThreadedComment)
    colls = Collaboration.objects.filter(_parent=parent,
                                         content_type=content_type,
                                         object_pk__isnull=False)
    return [c.content_object for c in colls if c.content_object is not None]


def pretty_date(timestamp):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    diff = now - timestamp

    second_diff = diff.seconds
    day_diff = diff.days
    ago = ""

    if day_diff == 0:
        if second_diff < 60:
            ago = str(second_diff) + " seconds ago"
        elif second_diff < 120:
            ago = "a minute ago"
        elif second_diff < 3600:
            ago = str(second_diff / 60) + " minutes ago"
        elif second_diff < 86400:
            ago = str(second_diff / 3600) + " hour(s) ago"

        return "%s (%s)" % (timestamp.strftime("%I:%M %p"), ago)
    elif day_diff == 1:
        ago = "(Yesterday)"
    elif day_diff < 14:
        ago = "(" + str(day_diff) + " days ago)"

    return "%s %s" % (timestamp.strftime("%m/%d/%Y %I:%M %p"), ago)
