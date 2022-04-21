from functools import total_ordering, cmp_to_key

from django.utils.encoding import smart_text
from django_comments.models import Comment
from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.projects.models import Project
from mediathread.util import cmp
from structuredcollaboration.models import Collaboration


def adapt_date(obj):
    date_fields = ('submit_date', 'modified', 'added',)
    return [getattr(obj, d) for d in date_fields if hasattr(obj, d)][0]


class Clumper(object):
    """Clumps stuff by thing.content_object"""
    stuff = None  # don't make array here or it persists to other requests.
    items = None

    def __init__(self, *feeds, **kwargs):
        self.items = {}
        group_by = kwargs.get('group_by', None)
        for feed in feeds:
            for item in feed:
                parent = self.ClumpItem.parent_object(item, group_by)
                if parent in self.items:
                    self.items[parent].append(item)
                else:
                    self.items[parent] = self.ClumpItem(item,
                                                        group_by=group_by)

    def __len__(self):
        # used to be each unclumped-item, but...why?
        return len(self.items)

    def __iter__(self):
        # will use ClumpItem.__cmp__
        return iter(sorted(self.items.values()))

    @total_ordering
    class ClumpItem(object):
        things = None
        primary_thing = None

        def __init__(self, thingie, primary=None, group_by=None):
            self.things = []
            self.things.append(thingie)
            self.primary = primary
            self.group_by = group_by

        def __eq__(self, other):
            return self.order_by(self.things[0], other.things[0]) == 0

        def __ne__(self, other):
            return not (self == other)

        def __lt__(self, other):
            return self.order_by(self.things[0], other.things[0]) < 0

        def __str__(self):
            return smart_text(self.things[0])

        def append(self, obj):
            if len(self.things) < 4:
                if obj not in self.things:  # no dups
                    self.things.append(obj)
                    self.things.sort(key=cmp_to_key(self.order_by))

        @staticmethod
        def order_by(obj_a, obj_b):
            """newest first w/support for Comment and SherdNote, Project"""
            a_date = adapt_date(obj_a)
            b_date = adapt_date(obj_b)
            return cmp(b_date, a_date)

        @property
        def add_only(self):
            return (len(self.things) == 1 and isinstance(self.things[0],
                                                         Asset))

        @classmethod
        def parent_object(cls, thingie, group_by=None):
            if hasattr(thingie, 'clump_parent'):
                return thingie.clump_parent(group_by)
            else:
                return getattr(thingie, 'content_object', None)

        @property
        def content_object(self):
            return self.parent_object(self.things[0], self.group_by)

        @property
        def href(self):
            if self.add_only or isinstance(self.content_object, Collaboration):
                parent = self.content_object.get_parent()
                if parent and isinstance(parent.content_object, Project):
                    return parent.content_object.get_absolute_url()
                else:
                    return getattr(self.things[0], 'get_parent_url',
                                   self.things[0].get_absolute_url)()
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
            if isinstance(thing, Project):
                return None
            if isinstance(thing, SherdNote):
                return None
            return getattr(thing, 'body',
                           getattr(thing, 'comment', None) or getattr(thing,
                                                                      'title',
                                                                      None))

        @staticmethod
        def adapt_user(thing):
            return getattr(thing, 'author',
                           getattr(thing, 'user', getattr(thing,
                                                          'participant',
                                                          None)))

        @staticmethod
        def adapt_action(thing):
            amap = {Comment: 'discussed',
                    SherdNote: 'analyzed',
                    Asset: 'added',
                    Project: 'updated',
                    DiscussionIndex: 'discussed', }
            return amap.get(type(thing), 'notes')

        def adapt_href(self, thing):
            if isinstance(thing, Comment):
                return None
            if isinstance(thing, SherdNote) and thing.range1 is None:
                return None

            if isinstance(self.content_object, Collaboration):
                if hasattr(thing.content_object, "get_top_ancestor"):
                    parent = thing.content_object.get_top_ancestor()
                    if parent and isinstance(parent.content_object, Project):
                        return None

            if hasattr(thing, 'get_absolute_url'):
                return thing.get_absolute_url()

            return self.content_object.get_absolute_url()

        def __iter__(self):
            """returns strings for each interesting thingie"""
            return iter([{'user': self.adapt_user(i),
                          'action': self.adapt_action(i),
                          'href': self.adapt_href(i),
                          'text': self.adapt_str(i),
                          'date': adapt_date(i)}
                         for i in self.things])

        def __getitem__(self, k):
            return self.things[k]
