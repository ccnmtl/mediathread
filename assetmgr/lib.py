import simplejson

from urlparse import urlsplit
import urllib2

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

def most_popular(assets):
    """
    considers popularity == number of distinct users who annotated
    the asset in any way (tag, global annotation, clip, etc)
    """
    most_popular = {}
    for asset in assets:
        users_who_annotated_it = {}
        for annotation in asset.sherdnote_set.all():
            if not users_who_annotated_it.has_key(annotation.author):
                users_who_annotated_it[annotation.author] = 0
            users_who_annotated_it[annotation.author] += 1
        popularity = len(users_who_annotated_it)
        setattr(asset, 'popularity', popularity)
        most_popular.setdefault(popularity, []).append(asset)

    pop_hash = most_popular
    most_popular = []
    for count, assets in reversed(pop_hash.items()):
        most_popular.extend(assets)
    return most_popular


def get_metadata(asset, authenticate=False, **auth_info):
    """
    gets metadata for the asset and saves it to the database in a json dict

    if `authenticate` is True, then HTTP Basic Authentication will be used
    with realm, user and passwd information passed in as kwargs.

    important notes about the current implementation:
     * it's extremely coupled to the openvault site. it will not work for
       any assets that were not taken from the openvault site, period.
     * it blindly makes an http request to the asset url. so this really
       should not be done synchronously. it's being done synchronously.
     * it currently only stores the asset description. other metadata can
       be added as needed.
     * it does a screenscrape of the html. did i mention it's coupled to
       the openvault implementation?
    """

    html_content = asset.html_source
    # ^^ will error if there is more than one hit, i think?

    if not html_content:
        # i dunno. `url` might ought to just be a required source?
        return

    url = html_content.url
    base_href = urlsplit(url)
    base_href = "%s://%s" % (base_href[0], base_href[1])

    if authenticate:
        # set up authentication info
        authinfo = urllib2.HTTPBasicAuthHandler()
        authinfo.add_password(realm=auth_info['realm'],
                              uri=base_href,
                              user=auth_info['user'],
                              passwd=auth_info['passwd'])
    
        # build a new opener that adds authentication and install it
        opener = urllib2.build_opener(authinfo)
        urllib2.install_opener(opener)

    f = urllib2.urlopen(url)

    assert f.code == 200

    body = f.read()
    import lxml.html

    fragment = lxml.html.fromstring(body)
    fragment.make_links_absolute(base_href)

    metadatas = fragment.cssselect("div.metadata.primary>ul>li")
    metadata_dict = {}

    try:
        metadata_dict['citation'] = _get_metadata_citation(fragment)
    except IndexError:
        pass
        
    for metadata in metadatas:
        try:
            key = metadata.cssselect('h3')[0].text
        except IndexError:
            continue
        # here's hopin' bvault is ready.  maria says yes
        if key == "Description":
            metadata_dict['description'] = \
                _get_metadata_description(metadata)
            continue
        if key == "Related":
            related = _get_metadata_related(metadata)
            if related:
                metadata_dict['segments in this record'] = related
            pass

    #assert metadata_dict.has_key('description')
    #assert metadata_dict.has_key('related')

    metadata = simplejson.dumps(metadata_dict)
    asset.metadata_blob = metadata
    asset.save()

    return metadata

def _get_metadata_citation(html, format=None):

    if format is None:
        format = 'chicago'

    citation = html.cssselect("div.citation#cite_%s" % format)
    citation = citation[0].text_content()
    return citation.replace('<', '&lt;').replace('>', '&gt;')

# XXX TODO: just pass in the whole html fragment, dude
def _get_metadata_related(metadata):
    metadatas = metadata.cssselect("div.content ul>li>div.hentry")
    from lxml.html import tostring

    if len(metadatas):
        return ''.join(tostring(metadata).replace('\n', '') 
                       for metadata in metadatas)
    else:
        return None

# XXX TODO: just pass in the whole html fragment, dude
def _get_metadata_description(metadata):

    metadatas = metadata.cssselect("div.content>div")

    description = None
    for metadata in metadatas:
        key = metadata.getchildren()[0]
        if key.tag.upper() != "STRONG":
            continue
        if not key.text.endswith("Description:"):
            continue
        description = metadata.text_content()[len(key.text):]
        break

    assert description is not None
    return description


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


