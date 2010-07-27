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

    def __unicode__(self):
        return self.policy_name

    def __eq__(self,other):
        return self == other or self.policy_name == other

DEFAULT_POLICY = getattr(settings,'DEFAULT_COLLABORATION_POLICY',PublicEditorsAreOwners())

class Collaboration(models.Model):
    objects = CollaborationManager()
    user = models.ForeignKey(User,null=True, blank=True)
    group = models.ForeignKey(Group,null=True, blank=True)

    title = models.CharField(max_length=1024,null=True,default=None)
    slug = models.SlugField(max_length=50,null=True,default=None, blank=True)
    
    # Content-object field
    content_type   = models.ForeignKey(ContentType,
                                       related_name="collaboration_set_for_%(class)s",
                                       null=True, blank=True)
    object_pk      = models.TextField(_('object ID'),null=True, blank=True)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")


    _policy = models.ForeignKey(CollaborationPolicyRecord,null=True,default=None, blank=True)
    
    _parent = models.ForeignKey('self',related_name='children',null=True,default=None, blank=True)

    #will eventually be used instead of _parent
    context = models.ForeignKey('self',related_name='context_children',null=True,default=None, blank=True)

    def save(self,*args,**kwargs):
        create_group = (self.group and not self.group.id)
        
        super(Collaboration,self).save(*args,**kwargs)
        if create_group:
            self.have_group()

    def have_group(self):
        if self.id:
            if self.group_id:
                return self.group
            else:
                self.group = Group.objects.create(name='Collaboration %s: %s' % (self.pk, self.title))
                self.save()
                return self.group

    def inc_order():
        return Collaboration.objects.inc_order()

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
        return self.policy.permission_to(self,permission,request)


    def get_parent(self):
        return self._parent

    def get_top_ancestor(self): #i.e. domain
        result = self
        while result.get_parent():
            result = result.get_parent()
        return result
        

    def append_child(self,object=None):
        coll, created = Collaboration.objects.get_or_create(_parent=self,
                                                            content_type=ContentType.objects.get_for_model(type(object)),
                                                            object_pk=str(object.pk),
                                                            )
        return coll
        
    def get_policy(self):
        return self._policy_id and self._policy.policy or DEFAULT_POLICY
    def set_policy(self,p):
        self._policy, created = CollaborationPolicyRecord.objects.get_or_create(policy_name=p)
    policy = property(get_policy,set_policy)


    @classmethod
    def get_associated_collab(cls, obj):
        """
        collaboration, if any, associated with this object:
        Collaboration.get_associated_collabs(my_course)
        """
        #import pdb
        #pdb.set_trace()
        ct = ContentType.objects.get_for_model(type(obj))
        return Collaboration.objects.get(
            content_type=ct,
            object_pk=str(obj.pk)
        )
        

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

    
    def __unicode__(self):
        return u'%s %r <%s %s> [%s]' % (self.title, self.pk, self.content_type, 
                                        self.object_pk, self.slug)
