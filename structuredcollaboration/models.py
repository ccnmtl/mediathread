from django.db import models
from django.db.models import get_model,Max
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.conf import settings
from structuredcollaboration.policies import CollaborationPolicies,PublicEditorsAreOwners
from django.utils.translation import ugettext_lazy as _

User = get_model('auth','user')
Group = get_model('auth','group')

class CollaborationManager(models.Manager):
    def inc_order(self):
        return 1 + (self.aggregate(Max('_order')).get('_order__max',0) or 0)

    
class CollaborationPolicyRecord(models.Model):
    policy_name = models.CharField(max_length=512, choices=CollaborationPolicies)
    
    @property
    def policy(self):
        return CollaborationPolicies.registered_policies[self.policy_name]

DEFAULT_POLICY = getattr(settings,'DEFAULT_COLLABORATION_POLICY',PublicEditorsAreOwners())

class Collaboration(models.Model):
    objects = CollaborationManager()
    user = models.ForeignKey(User,null=True)
    group = models.ForeignKey(Group,null=True)

    title = models.CharField(max_length=1024,null=True,default=None)
    slug = models.SlugField(max_length=50,null=True,default=None)
    
    # Content-object field
    content_type   = models.ForeignKey(ContentType,
                                       related_name="collaboration_set_for_%(class)s",
                                       null=True)
    object_pk      = models.TextField(_('object ID'),null=True)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    #when content_object is a modelversion of another type, then versioned_pk
    #is a pointer to the versioned object (while object_pk points to the specific version)
    versioned_pk      = models.TextField(_('versioned ID'),null=True)

    _policy = models.ForeignKey(CollaborationPolicyRecord,null=True,default=None)
    
    _parent = models.ForeignKey('self',related_name='children',null=True,default=None)

    #will eventually be used instead of _parent
    context = models.ForeignKey('self',related_name='context_children',null=True,default=None)

    def inc_order():
        return Collaboration.objects.inc_order()
    #autofield must have primary_key=true Dumb!
    _order = models.IntegerField(default=inc_order)
    

    class Meta:
        unique_together = (("content_type", "object_pk"),)
        ordering = ['-_order']
        
    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return urlresolvers.reverse(
            "comments-url-redirect",
            args=(self.content_type_id, self.object_pk)
        )

    def permission_to(self,permission,request):
        policy = self._policy_id and self._policy.policy or DEFAULT_POLICY
        return policy.permission_to(self,permission,request)


    def get_parent(self):
        pass

    def get_top_ancestor(self): #i.e. domain
        pass

    def append_child(self,object=None):
        coll, created = Collaboration.objects.get_or_create(_parent=self,
                                                            content_type=ContentType.objects.get_for_model(type(object)),
                                                            object_pk=str(object.pk),
                                                            )
        return coll

    #these methods are for optimized recursive structures
    #while for other cases, we optimize for shallow structures
    #think of it as the datastructure equivalent to tail-recursion :-)
    def get_ancestor_different_type(self):
        """
        returns first ancestor that is a different type from self
        """
        pass

    def get_ancestor_same_type(self):
        """
        returns last ancestor of the same type in a continuous chain
        """
        pass

    
