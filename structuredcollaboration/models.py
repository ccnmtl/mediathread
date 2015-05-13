from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.conf import settings
from structuredcollaboration.policies import CollaborationPolicies
from structuredcollaboration.policies import PublicEditorsAreOwners
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User, Group


class CollaborationManager(models.Manager):
    def get_for_object_list(self, object_list):
        ctype = ContentType.objects.get_for_model(object_list[0])
        ids = [str(o.id) for o in object_list]
        lst = self.filter(content_type__pk=ctype.pk, object_pk__in=ids)
        return lst

    def get_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        return self.get(content_type__pk=ctype.pk, object_pk=str(obj.pk))


class CollaborationPolicyRecord(models.Model):
    policy_name = models.CharField(max_length=512,
                                   choices=CollaborationPolicies)

    @property
    def policy(self):
        return CollaborationPolicies.registered_policies[self.policy_name]

    def __unicode__(self):
        return self.policy_name

    def __eq__(self, other):
        return self.policy_name is other or self is other

DEFAULT_POLICY = getattr(settings,
                         'DEFAULT_COLLABORATION_POLICY',
                         PublicEditorsAreOwners())


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

    object_pk = models.CharField(_('object ID'),
                                 max_length=255,
                                 null=True,
                                 blank=True)

    content_object = generic.GenericForeignKey(ct_field="content_type",
                                               fk_field="object_pk")

    policy_record = models.ForeignKey(CollaborationPolicyRecord,
                                      null=True, default=None, blank=True)

    _parent = models.ForeignKey('self',
                                related_name='children',
                                null=True,
                                default=None,
                                blank=True)

    context = models.ForeignKey('self',
                                related_name='context_children',
                                null=True,
                                default=None,
                                blank=True)

    def save(self, *args, **kwargs):
        create_group = (self.group and not self.group.id)

        super(Collaboration, self).save(*args, **kwargs)
        if create_group:
            self.have_group()

    def have_group(self):
        if self.id:
            if self.group_id:
                return self.group
            else:
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

    def permission_to(self, permission, request):
        rv = self.policy.permission_to(self, permission, request)
        return rv

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
        return (self.policy_record and self.policy_record.policy or
                DEFAULT_POLICY)

    def set_policy(self, p):
        if p is None:
            self.policy_record = None
        else:
            self.policy_record, created = \
                CollaborationPolicyRecord.objects.get_or_create(policy_name=p)

    policy = property(get_policy, set_policy)

    def __unicode__(self):
        return u'%s %r <%s %s> [%s]' % (self.title, self.pk, self.content_type,
                                        self.object_pk, self.slug)
