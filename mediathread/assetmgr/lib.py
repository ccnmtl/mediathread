from mediathread.djangosherd.models import SherdNote
from tagging.models import TaggedItem
import datetime


def tag_filter_for():
    def tag_filter(asset, tag_string, user):
        notes = TaggedItem.objects.get_union_by_model(asset.sherdnote_set,
                                                      tag_string)
        return len(notes) > 0
    return tag_filter


def date_filter_for(attr):

    def date_filter(asset, date_range, user):
        """
        we want the added/modified date *for the user*, ie when the
        user first/last edited/created an annotation on the asset --
        not when the asset itself was created/modified.

        this is really really ugly.  wouldn't be bad in sql but i don't
        trust my sql well enough. after i write some tests maybe?
        """
        if attr == "added":
            annotations = SherdNote.objects.filter(asset=asset, author=user)
            annotations = annotations.order_by('added')
            # get the date on which the earliest annotation was created
            date = annotations[0].added

        elif attr == "modified":
            if user:
                annotations = SherdNote.objects.filter(asset=asset,
                                                       author=user)
            else:
                annotations = SherdNote.objects.filter(asset=asset)

            # get the date on which the most recent annotation was created
            annotations = annotations.order_by('-added')
            added_date = annotations[0].added
            # also get the most recent modification date of any annotation
            annotations = annotations.order_by('-modified')
            modified_date = annotations[0].modified

            if added_date > modified_date:
                date = added_date
            else:
                date = modified_date

        date = datetime.date(date.year, date.month, date.day)

        today = datetime.date.today()

        if date_range == 'today':
            return date == today
        if date_range == 'yesterday':
            before_yesterday = today + datetime.timedelta(-2)
            return date > before_yesterday and date < today
        if date_range == 'lastweek':
            over_a_week_ago = today + datetime.timedelta(-8)
            return date > over_a_week_ago
    return date_filter


filter_by = {
    'tag': tag_filter_for(),
    'added': date_filter_for('added'),
    'modified': date_filter_for('modified')
}


# NON_VIEW
def get_active_filters(request, filter_by=filter_by):
    return dict((filter, request.GET.get(filter))
                for filter in filter_by
                if filter in request.GET)
