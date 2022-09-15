import importlib

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text


class CollaborationPolicyRecord(models.Model):
    policy_name = models.CharField(max_length=512)

    def __str__(self):
        return self.policy_name

    def __eq__(self, other):
        return self.policy_name is other or self is other

    @classmethod
    def class_for_name(cls, class_name):
        # load the module, will raise ImportError if module cannot be loaded
        m = importlib.import_module('structuredcollaboration.policies')
        # get the class, will raise AttributeError if class cannot be found
        c = getattr(m, class_name)
        return c

    def policy_instance(self):
        return self.class_for_name(self.policy_name)()


class CollaborationManager(models.Manager):
    def get_for_object_list(self, object_list):
        if len(object_list) < 1:
            return Collaboration.objects.none()
        else:
            model_name = object_list[0]._meta.model.__name__.lower()
            ids = [o.id for o in object_list]

            prefetch = ['user', 'group', 'context', 'content_object',
                        '_parent', 'policy_record']
            return self.filter(content_type__model=model_name,
                               object_pk__in=ids).prefetch_related(*prefetch)

    def get_for_object(self, obj):
        model_name = obj._meta.model.__name__.lower()
        return self.select_related(
            'user', 'group', '_parent', 'policy_record').get(
            content_type__model=model_name, object_pk=obj.pk)


class Collaboration(models.Model):
    objects = CollaborationManager()
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    group = models.ForeignKey(
        Group, null=True, blank=True, on_delete=models.CASCADE)

    title = models.CharField(max_length=1024, null=True, default=None)
    slug = models.SlugField(
        max_length=1024, null=True, default=None, blank=True)

    # Content-object field
    content_type = models.ForeignKey(
        ContentType, related_name="collaboration_set_for_%(class)s",
        null=True, blank=True, on_delete=models.CASCADE)

    object_pk = models.IntegerField(
        _('object ID'), null=True, blank=True)

    content_object = GenericForeignKey(ct_field="content_type",
                                       fk_field="object_pk")

    policy_record = models.ForeignKey(
        CollaborationPolicyRecord,
        null=True, default=None, blank=True, on_delete=models.CASCADE)

    _parent = models.ForeignKey(
        'self', related_name='children',
        null=True, default=None, blank=True, on_delete=models.CASCADE)

    context = models.ForeignKey(
        'self', related_name='context_children',
        null=True, default=None, blank=True, on_delete=models.CASCADE)

    def get_or_create_group(self):
        if not self.group:
            name = smart_text('Collaboration %s: %s' %
                              (self.pk, self.title))[0:80]
            self.group = Group.objects.create(name=name)
            self.save()
        return self.group

    class Meta:
        unique_together = (("content_type", "object_pk"),)
        ordering = ['title']

    def get_content_object_url(self):
        "Get a URL suitable for redirecting to the content object."
        return reverse(
            "comments-url-redirect",
            args=(self.content_type_id, self.object_pk)
        )

    def get_absolute_url(self):
        return reverse("collaboration-obj-view",
                       args=(self.context.slug,
                             self.content_type.model,
                             self.object_pk))

    def permission_to(self, permission, course, user):
        return self.get_policy().permission_to(self, permission,
                                               course, user)

    def get_parent(self):
        return self._parent

    def get_children_for_object(self, obj):
        model_name = obj._meta.model.__name__.lower()
        return self.children.filter(
                content_type__model=model_name
            ).prefetch_related('content_object', 'policy_record', 'user')

    def get_top_ancestor(self):  # i.e. domain
        result = self
        while result.get_parent():
            result = result.get_parent()
        return result

    def append_child(self, obj):
        coll, created = Collaboration.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(type(obj)),
            object_pk=str(obj.pk), )
        coll._parent = self
        coll.save()
        return coll

    def remove_children(self):
        children = Collaboration.objects.filter(_parent=self)
        for child in children:
            child._parent = None
            child.save()

    def get_policy(self):
        if not self.policy_record:
            policy_name = getattr(settings, 'DEFAULT_COLLABORATION_POLICY',
                                  'PublicEditorsAreOwners')
            self.set_policy(policy_name)
            self.save()
        return self.policy_record.policy_instance()

    def set_policy(self, policy_name):
        if policy_name is None:
            self.policy_record = None
        else:
            self.policy_record, created = \
                CollaborationPolicyRecord.objects.get_or_create(
                    policy_name=policy_name)

        self.save()

    def __str__(self):
        return u'%s %r <%s %s> [%s]' % (self.title, self.pk, self.content_type,
                                        self.object_pk, self.slug)
