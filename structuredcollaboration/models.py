from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models
from django.utils.translation import ugettext_lazy as _


DEFAULT_POLICY = getattr(settings, 'DEFAULT_COLLABORATION_POLICY',
                         'PublicEditorsAreOwners')


class CollaborationPolicyRecordManager(models.Manager):
    '''
        @todo - consider pulling this whole registration approach.
        feels overcomplicated & unnecessary. The primary aim here
        seems to be caching instances of the policies.
    '''
    registered_policies = dict()

    def policy_instance(self, record):
        return self.registered_policies[record.policy_name]

    def register_policy(self, policy_class, policy_key, policy_title):
        self.registered_policies[policy_key] = policy_class()


class CollaborationPolicyRecord(models.Model):
    objects = CollaborationPolicyRecordManager()
    policy_name = models.CharField(max_length=512)

    def __unicode__(self):
        return self.policy_name

    def __eq__(self, other):
        return self.policy_name is other or self is other


class CollaborationManager(models.Manager):
    def get_for_object_list(self, object_list):
        if len(object_list) < 1:
            return Collaboration.objects.none()
        else:
            ctype = ContentType.objects.get_for_model(object_list[0])
            ids = [str(o.id) for o in object_list]
            return self.filter(
                content_type=ctype,
                object_pk__in=ids).select_related('user', 'group',
                                                  'policy_record')

    def get_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        return self.select_related('user', 'group', 'policy_record').get(
            content_type=ctype, object_pk=str(obj.pk))


class Collaboration(models.Model):
    objects = CollaborationManager()
    user = models.ForeignKey(User, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)

    title = models.CharField(max_length=1024, null=True, default=None)
    slug = models.SlugField(max_length=50, null=True, default=None, blank=True)

    # Content-object field
    content_type = models.ForeignKey(
        ContentType, related_name="collaboration_set_for_%(class)s",
        null=True, blank=True)

    object_pk = models.CharField(_('object ID'), max_length=255,
                                 null=True, blank=True)

    content_object = generic.GenericForeignKey(ct_field="content_type",
                                               fk_field="object_pk")

    policy_record = models.ForeignKey(CollaborationPolicyRecord,
                                      null=True, default=None, blank=True)

    _parent = models.ForeignKey('self', related_name='children',
                                null=True, default=None, blank=True)

    context = models.ForeignKey('self', related_name='context_children',
                                null=True, default=None, blank=True)

    def get_or_create_group(self):
        if not self.group:
            name = unicode('Collaboration %s: %s' %
                           (self.pk, self.title))[0:80]
            self.group = Group.objects.create(name=name)
            self.save()
        return self.group

    class Meta:
        unique_together = (("content_type", "object_pk"),)
        ordering = ['title']

    def get_content_object_url(self):
        "Get a URL suitable for redirecting to the content object."
        return urlresolvers.reverse(
            "comments-url-redirect",
            args=(self.content_type_id, self.object_pk)
        )

    def get_absolute_url(self):
        if self.context_id and self.context.slug:
            return urlresolvers.reverse("collaboration-obj-view",
                                        args=(self.context.slug,
                                              self.content_type.model,
                                              self.object_pk))
        else:
            return urlresolvers.reverse("collaboration-dispatch",
                                        args=(self.pk,))

    def permission_to(self, permission, course, user):
        return self.get_policy().permission_to(self, permission,
                                               course, user)

    def get_parent(self):
        return self._parent

    def get_top_ancestor(self):  # i.e. domain
        result = self
        while result.get_parent():
            result = result.get_parent()
        return result

    def append_child(self, obj=None):
        coll, created = Collaboration.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(type(obj)),
            object_pk=str(obj.pk), )
        coll._parent = self
        coll.save()
        return coll

    def get_policy(self):
        if self.policy_record:
            return CollaborationPolicyRecord.objects.policy_instance(
                self.policy_record)
        else:
            record, created = CollaborationPolicyRecord.objects.get_or_create(
                policy_name=DEFAULT_POLICY)
            return CollaborationPolicyRecord.objects.policy_instance(record)

    def set_policy(self, policy_name):
        if policy_name is None:
            self.policy_record = None
        else:
            self.policy_record, created = \
                CollaborationPolicyRecord.objects.get_or_create(
                    policy_name=policy_name)

    def __unicode__(self):
        return u'%s %r <%s %s> [%s]' % (self.title, self.pk, self.content_type,
                                        self.object_pk, self.slug)
