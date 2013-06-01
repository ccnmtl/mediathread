from structuredcollaboration.models import Collaboration
from django.contrib.contenttypes.models import ContentType
from threadedcomments import ThreadedComment


class CollaborationThreadedComment_Migration1:
    """
    The first implementation connected things like this:
    threadedcomment -> collaboration -> _parent -> object
    The new way will be:
    threadedcomment -> collaboration -> _parent -> object
                                     -> threadedcomment
    """
    harmless = True

    def run(self):
        collab_type = ContentType.objects.get_for_model(Collaboration)
        root_comments = \
            ThreadedComment.objects.filter(parent=None,
                                           content_type=collab_type)
        for root in root_comments:
            disc_sc = root.content_object
            disc_sc.content_object = root
            disc_sc.save()

    def reverse(self):
        collab_type = ContentType.objects.get_for_model(Collaboration)
        root_comments = \
            ThreadedComment.objects.filter(parent=None,
                                           content_type=collab_type)
        for root in root_comments:
            disc_sc = root.content_object
            disc_sc.content_object = None
            disc_sc.save()


class CollaborationThreadedComment_Migration2:
    """NEVER USED YET: CONSIDERING....
       First implementation connected things like this:
       threadedcomment -> collaboration -> _parent -> object
       The new way will be:
       collaboration -> threadedcomment -> object
                     -> _parent -> object
       The advantage is mostly that the collaboration
       knows what it's protecting

       This script moves the pointers around
    """
    harmless = False

    def run(self):
        collab_type = ContentType.objects.get_for_model(Collaboration)
        root_comments = \
            ThreadedComment.objects.filter(parent=None,
                                           content_type=collab_type)
        for root in root_comments:
            disc_sc = root.content_object
            target_object = disc_sc._parent.content_object
            child_comments = \
                ThreadedComment.objects.filter(content_type=collab_type,
                                               object_pk=disc_sc.pk)
            for child in child_comments:
                child.content_object = target_object
                child.save()

            disc_sc.content_object = root
            disc_sc.save()
            root.content_object = target_object
            root.save()

    def reverse(self):
        comm_type = ContentType.objects.get_for_model(ThreadedComment)
        comment_collabs = Collaboration.objects.filter(content_type=comm_type)
        for disc_sc in comment_collabs:
            target_object = disc_sc._parent.content_object
            root = disc_sc.content_object
            target_type = \
                ContentType.objects.get_for_model(target_object.__class__)
            child_comments = \
                ThreadedComment.objects.filter(content_type=target_type,
                                               object_pk=target_object.pk)
            for child in child_comments:
                child.content_object = disc_sc
                child.save()
            disc_sc.content_object = None
            disc_sc.save()
            root.content_object = disc_sc
            root.save()


class Discussion:
    migrations = (CollaborationThreadedComment_Migration1(),)
