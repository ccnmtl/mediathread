import simplejson

from django.db import models
from django.conf import settings

Tag = models.get_model('tagging','tag')
User = models.get_model('auth','user')
Group = models.get_model('auth','group')
Course = models.get_model('courseaffils','course')

def default_url_processor(source,request):
    return source.url

url_processor = getattr(settings,'ASSET_URL_PROCESSOR',default_url_processor)

class AssetManager(models.Manager):
    def get_by_args(self, args, **constraints):
        "args typically is request.GET"
        criteria = Asset.good_args(args)
        if not criteria:
            return False

        q = reduce(lambda x,y:x|y, #composable Q's
                   [models.Q(label=k,url=args[k], primary=True) 
                    for k in criteria])
        sources = Source.objects.filter(q, **constraints)
        if sources:
            return sources[0].asset
        else:
            return None

    def archives(self):
        return self.filter(source__primary=True,
                           source__label='archive'
                           )
                           
    @property
    def dir(self):
        return dir(self)

class Asset(models.Model):
    objects = AssetManager() #custom manager
    
    added = models.DateTimeField('date created', editable=False, auto_now_add=True)
    modified = models.DateTimeField('date modified', editable=False, auto_now=True)    

    author = models.ForeignKey(User)
    course = models.ForeignKey(Course)

    active = models.BooleanField(default=True)

    title = models.CharField(max_length=1024)

    #make it json or somethin
    metadata_blob = models.TextField(blank=True,
                                     help_text="""Be careful, this is a JSON blob and NOT a place to enter the description, etc, and is easy to format incorrectly.  Make sure not to add any "'s.""")

    #labels which determine the saving of an asset
    #in order of priority for which label is marked primary
    #an asset must have at least one source label from this list
    #'url' should probably stay at the end
    useful_labels = ('flv', 'flv_pseudo', 'flv_rtmp', 'mp4', 'mp4_pseudo', 'mp4_rtmp',
                     'youtube','quicktime','realplayer', 'ogg', 
                     'video_pseudo','video_rtmp','video',#unknown format, but we can try to play
                     'mp3',
                     'image_fpx', #artstor.org and FSI flash image viewer in general
                     'image')

    #not good for uniqueness
    fundamental_labels = ('archive','url',)
    primary_labels = useful_labels + fundamental_labels

    @classmethod
    def good_args(cls, args):
        return set(cls.primary_labels) & set(args.keys())

    def __unicode__(self):
        return u'%s <%r> (%s)' % (self.title, self.pk, self.course.title)

    def metadata(self):
        if self.metadata_blob:
            try:
                return simplejson.loads(str(self.metadata_blob))
            except: #presumably json decoding, but let's quiet everything
                return {}
        return {}

    def saved_by(self):
        return self.author

    @models.permalink
    def get_absolute_url(self):
        return ('asset-view', (), {
                'asset_id': self.pk,
                })

    @property
    def html_source(self):
        return Source.objects.get(asset=self, label='url')

    @property
    def sources(self):
        return dict([(s.label,s) for s in Source.objects.filter(asset=self) ])

    @property
    def primary(self):
        return Source.objects.get(asset=self,primary=True)

    def tags(self):
        return Tag.objects.usage_for_queryset(self.sherdnote_set.all())

    def global_annotation(self, user, auto_create=True):
        SherdNote = models.get_model('djangosherd','sherdnote')
        if SherdNote:
            return SherdNote.objects.global_annotation(self, user, auto_create=auto_create)[0]

    def save_tag(self, user, tag):
        """ 
        adds a single tags to asset by user. if the user has already
        annotated the asset with this tag, this function does nothing.
        
        returns True iff this is the first time the given user
        is tagging the asset .. though it'd be nicer to return
        whether this function actually did anything.
        """
        SherdNote = models.get_model('djangosherd','sherdnote')
        if SherdNote:
            bucket, created = SherdNote.objects.global_annotation(self, user)
            bucket.add_tag(tag)
            bucket.save()        
            return created
    @property
    def dir(self):
        return dir(self)

    request = None
    def sherd_json(self,request=None):
        sources = {}
        for s in self.source_set.all():
            sources[s.label] = {
                'label':s.label,
                'url':s.url_processed(request),
                'width':s.width,
                'height':s.height,
                'primary':s.primary
                }
        try:
            metadata = simplejson.loads(self.metadata_blob)
        except ValueError:
            metadata = None
        return {
            'sources':sources,
            'type':self.primary.label,
            'title':self.title, 
            'metadata':metadata,
            'local_url':self.get_absolute_url(),
            'id':self.pk,
            }
        
        
class Source(models.Model):
    asset = models.ForeignKey(Asset)

    #hint on source's nature, e.g. thumbnail
    #should be generally human readable
    label = models.CharField(max_length=64)

    #should this support URI fragments?
    #file:/// for local files?
    url = models.CharField(max_length=1024)

    #only one Source per asset should have primary=True
    #This should help indicate what 'kind' of thing
    #the asset is, so one with label 'quicktime' as primary
    #is a movie, even though it might have image urls for thumbs, etc
    primary = models.BooleanField(default=False)

    media_type = models.CharField(default=None,null=True,max_length=64)

    #in bytes (like FileField)
    size = models.PositiveIntegerField(default=0)

    #obvious for visual media
    # you can hack this to use it for things like
    # multi-dimensional sizes: e.g. wordcount
    height = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)
    
    modified = models.DateTimeField('date modified', editable=False, auto_now=True)

    def __unicode__(self):
        asset = u'No Asset'
        if self.asset_id: #defensive for non-saved sources w/o an asset
            asset = self.asset
        return u'[%s] %s' % (self.label, unicode(asset))

    def is_image(self):
        return (self.label=='poster' or self.media_type.startswith('image/'))

    request = None
    def url_processed(self,request=None):
        if request is None:
            request = self.request or self.asset.request
        return url_processor(self,request)
        
    @property
    def dir(self):
        return dir(self)
    
