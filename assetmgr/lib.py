from urlparse import urlsplit
import urllib2
from courseaffils.lib import get_public_name
from djangosherd.models import SherdNote
from tagging.models import Tag

def annotated_by(assets, user, include_archives=False):
    fassets = assets.filter(
        sherdnote__author=user,sherdnote__range1=None).distinct().order_by('-sherdnote__modified').select_related()
    if include_archives:
        return fassets
    else:
        to_return = []
        for asset in fassets:
            #sky: why do this?  disabling for now
            #if nothing breaks for a bit, we'll drop it
            #if asset.sherdnote_set.filter(author=user).exclude(
            #    range1=None, range2=None, title=None,
            #    tags='', body=None).count() == 0:
            #    continue
            if asset.primary.label != 'archive':
                to_return.append(asset)
        return to_return

filter_by = {
    'tag': lambda asset, tag: filter(lambda x: x.name == tag,
                                     asset.tags()),
    #fake!!!
    'modified': lambda asset, text_date:asset,
}

#NON_VIEW
def get_active_filters(request, filter_by=filter_by):
    return dict((filter, request.GET.get(filter))
                for filter in filter_by
                if filter in request.GET)
