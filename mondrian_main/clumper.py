from django.db import models

Asset = models.get_model('assetmgr','asset')
SherdNote = models.get_model('djangosherd','sherdnote')
Project = models.get_model('projects','project')
User = models.get_model('auth','user')
#for portal
Comment = models.get_model('comments','comment')
ContentType = models.get_model('contenttypes','contenttype')

def adapt_date(b):
    date_fields = ('submit_date','modified','added',)
    return [getattr(b,d) for d in date_fields if hasattr(b,d)][0]

class Clumper():
    """Clumps stuff by thing.content_object"""
    stuff = None #don't make array here or it persists to other requests.
    items = None
    
    def __init__(self, *feeds):
        self.items = {}
        
        for f in feeds:
            for item in f:
                parent = self.ClumpItem.parent_object(item)
                if self.items.has_key(parent):
                    self.items[parent].append(item)
                else:
                    self.items[parent] = self.ClumpItem(item)

    def __len__(self):
        #used to be each unclumped-item, but...why?
        return len(self.items) 

    def __iter__(self):
        #will use ClumpItem.__cmp__
        return iter(sorted(self.items.values()))

    
    class ClumpItem():
        things = None
        primary_thing = None
        
        def __init__(self, thingie, primary=None):
            self.things = []
            self.things.append(thingie)
            self.primary=primary

        def __cmp__(self,other):
            return self.order_by(self.things[0],other.things[0])
            
        def __unicode__(self):
            return unicode(self.things[0])

        def append(self,obj):
            if len(self.things) < 4:
                if obj not in self.things: #no dups
                    self.things.append(obj)
                    self.things.sort(self.order_by)

        @staticmethod
        def order_by(a,b):
            """newest first w/support for Comment and SherdNote, Project"""
            a_date = adapt_date(a)
            b_date = adapt_date(b)
            return cmp(b_date, a_date)

        @property
        def add_only(self):
            return (len(self.things)==1 and isinstance(self.things[0],Asset))

        @classmethod
        def parent_object(cls,thingie):
            return getattr(thingie,'content_object',None)

        @property
        def content_object(self):
            return self.parent_object(self.things[0])

        @property
        def href(self):
            if self.add_only:
                return self.things[0].get_absolute_url()
            else:
                return self.content_object.get_absolute_url()
        @property
        def title(self):
            if self.add_only:
                return self.things[0].title
            else:
                return self.content_object.title

        @property
        def type(self):
            return self.content_object.__class__.__name__.lower()

        @staticmethod
        def adapt_str(thing):
            if isinstance(thing,Project): return None
            return getattr(thing,'comment',
                           getattr(thing,'title',None) or getattr(thing,'body',None)
                           )

        @staticmethod
        def adapt_user(thing):
            if isinstance(thing,Project): return None
            return getattr(thing,'author',
                           getattr(thing,'user',None))

        @staticmethod
        def adapt_action(thing):
            amap = {Comment:'discussed',
                    SherdNote:'analyzed',
                    Asset:'added',
                    Project:'updated',
                    }
            return amap.get(type(thing),'notes')

        def adapt_href(self,thing):
            if isinstance(thing,Comment): return None
            if isinstance(thing,SherdNote) and thing.range1 is None:
                return None            
            if hasattr(thing,'get_absolute_url'):
                return thing.get_absolute_url()
            else:
                return self.content_object.get_absolute_url()

        def __iter__(self):
            """returns strings for each interesting thingie"""
            return iter([{'user':self.adapt_user(i),
                          'action':self.adapt_action(i),
                          'href':self.adapt_href(i),
                          'text':self.adapt_str(i),
                          'date':adapt_date(i),
                          }
                         for i in self.things])

        def __getitem__(self,k):
            return self.things[k]
