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

def homepage_asset_json(request, asset, logged_in_user, record_owner, options):
    the_json = asset.sherd_json(request)
    
    if not options['selections_visible']:
        owners = [ request.user ]
        owners.extend(request.course.faculty)
        the_json['tags'] = tag_json(asset.filter_tags_by_users(owners))
    
    gannotation, created = SherdNote.objects.global_annotation(asset, record_owner or logged_in_user, auto_create=False)
    if gannotation and options['selections_visible']:
        the_json['global_annotation'] = gannotation.sherd_json(request, 'x', ('tags', 'body'))
        
    the_json['editable'] = options['can_edit']
    the_json['citable'] = options['citable']
    
    if options['selections_visible']:
        # @todo: refactor this serialization into a common place.
        def author_name(request, annotation, key):
            if not annotation.author_id:
                return None
            return 'author_name', get_public_name(annotation.author, request)
        def primary_type(request, annotation, key):
            return "primary_type", asset.primary.label
        annotations = []
        for ann in asset.sherdnote_set.filter(range1__isnull=False, author=record_owner):
            ann_json = ann.sherd_json(request, 'x', ('title', 'author', 'tags', author_name, 'body', 'modified', 'timecode', primary_type))
            ann_json['citable'] = options['citable']
            annotations.append(ann_json)
        the_json['annotations'] = annotations
        
    return the_json

def detail_asset_json(request, asset, options):
    asset_json = asset.sherd_json(request)
    asset_key = 'x_%s' % asset.pk
    
    ga = asset.global_annotation(request.user, False)
    asset_json['notes'] = ga.body if ga else ""
    
    if not options['selections_visible']:
        owners = [ request.user ]
        owners.extend(request.course.faculty)
        asset_json['tags'] = tag_json(asset.filter_tags_by_users(owners))

    annotations = [{
            'asset_key': asset_key,
            'range1': None,
            'range2': None,
            'annotation': None,
            'id': 'asset-%s' % asset.pk,
            'asset_id': asset.pk,
            }]
    
    if request.GET.has_key('annotations'):
        # @todo: refactor this serialization into a common place.
        def author_name(request, annotation, key):
            if not annotation.author_id:
                return None
            return 'author_name', get_public_name(annotation.author, request)
        for ann in asset.sherdnote_set.filter(range1__isnull=False):
            visible = options['selections_visible'] or request.user == ann.author or request.course.is_faculty(ann.author)
            if visible:     
                annotations.append(ann.sherd_json(request, 'x', ('title','author','tags',author_name,'body') ) )
    
    the_json = {
        'type': 'asset',
        'assets': { asset_key: asset_json }, #we make assets plural here to be compatible with the project JSON structure
        'annotations': annotations,
    }

    return the_json

def tag_json(tags):
    return [ { 'name': tag.name } for tag in tags ]
