def annotated_by(assets, user, include_archives=False):
    fassets = assets.filter(
        sherdnote__author=user, sherdnote__range1=None).distinct().order_by(
            '-sherdnote__modified').select_related()
    if include_archives:
        return fassets
    else:
        to_return = []
        for asset in fassets:
            if asset.primary.label != 'archive':
                to_return.append(asset)
        return to_return

filter_by = {
    'tag': lambda asset, tag: filter(lambda x: x.name == tag,
                                     asset.tags()),
    #fake!!!
    'modified': lambda asset, text_date: asset,
}


# NON_VIEW
def get_active_filters(request, filter_by=filter_by):
    return dict((filter, request.GET.get(filter))
                for filter in filter_by
                if filter in request.GET)
