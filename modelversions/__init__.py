"""
For questions or coments, please contact Robin Percy, rpercy at gmail dot com

modelversions provides a framework for maintaining a complete change history for specific models. 
To use it, require this module in your models.py and then issue a call to version_model(YourModelClass):
    eg. BookVersion = version_model(Book)
    
This will generate a second model named BookVersion which contains the same (non-primary key) fields as
Book, as well as a version_number and change_time field, which are populated automatically. The versions of a 
Book can be queried using book_instance.versions.filter(...)

version_model() also adds two new functions to the Book model: revert(), and get_latest_version(). revert() takes
an optional integer parameter indicating which version the object should be reverted to.  If negative the object
will be reverted back that many versions.  Note, to permanently revert an object, the object must be saved after
reverting.
"""
from django.db import models as m # need to rename models or django doesn't recognize app
from django.dispatch import dispatcher
from django.db.models.signals import post_save, pre_delete


from django.db.models import signals
from django.db.models.fields.related import RelatedField
from django.core.exceptions import ObjectDoesNotExist
import pdb, inspect

def version_model(model):
    """
    Based on the passed model, build a second model to store versioning information.
    Register functions to write version changes on save and delete of the original model
    NOTE: be sure to use strong references for signal connections so that inner funcs don't get
        garbage collected
    """
    version_model = _build_version_model(model)
    _decorate_model(model,version_model)
            
    def record_change(instance,change_type):
        version_instance = _version_from_instance(instance,version_model)
        version_instance.change_type = change_type  
        
        whether_to_save = True
        only_save_if_changed = False
        if hasattr (instance, 'only_save_if_changed' ):
            only_save_if_changed = instance.only_save_version_if_changed
        
        if only_save_if_changed and version_instance.version_number -2 > 0 and instance.versions[version_instance.version_number - 2]:
            older_instance = instance.versions[version_instance.version_number - 2]
            if hasattr (instance, 'only_save_version_if_changed_fields_to_ignore'):
                ignored = instance.only_save_version_if_changed_fields_to_ignore
            else:
                ignored = []
            
            fields_to_test = [f for f in _get_fields(instance).keys() if f not in ignored ]
            if [a for a in fields_to_test if getattr(version_instance, a)!= getattr(older_instance,a)] == []:
                whether_to_save = False
                #print "Unchanged so not saving"
                
        if whether_to_save:
            version_instance.save()    


    def record_save(sender,instance,signal, *args, **kwargs):
        # Record the save to the shadow table
        #pdb.set_trace()
        record_change(instance,"SAVE")
    post_save.connect(record_save, model, weak=False)
        
        
        
    def record_delete(sender,instance,signal,*args,**kwargs):
        # Record the delete to the shadow table
        record_change(instance,"DELETE")      
    pre_delete.connect(record_delete, model, weak=False)

    setattr(model,'version_model',version_model)

    return version_model


def undelete(model, id):
    """
    Returns a copy of the specified model as of it's last state before deleting
    """
    # If the object currently exists, just return it
    try:
        instance = model.objects.get(id=id)
        return instance
    except ObjectDoesNotExist:
        pass   
    
    # Try to rebuild from latest version
    try:      
        version = model.version_model.objects.filter(versioned_id=id).order_by('-version_number')[0]
        instance = model()
        _copy_instance_vals(version,instance)
        instance.id = id
        return instance
    except ObjectDoesNotExist,KeyError:
        return None
    


def _get_fields(model):
    """
    Returns a dict of field names and field objects for the model, excluding the pk field
    """
    return dict([ (field.name,field) for field in model._meta.fields if field.name != model._meta.pk.attname])

def _make_fields_versionable(fields):
    """
    Takes a dict of name:field pairs and converts foreign relations to
    versionable fields.
    """
    versionable_fields = {}
    for name in fields.keys():
        if isinstance(fields[name],RelatedField):
            # Instead of copying the FK, copy the attribute storing it's PK
            rel_pk = fields[name].rel.to._meta.pk
            if(isinstance(rel_pk,m.AutoField)):                
                # Don't want to auto increment the key, so convert to regular int
                versionable_fields[name] = m.IntegerField()
            else:
                # Respect custom PKs
                versionable_fields[name] = rel_pk
        else:
            versionable_fields[name] = fields[name]
    return versionable_fields

def _build_version_model(model):
    """
    Create a Shadow Model to store versioning info of model records
    """
    class Meta:        
        pass
        
    version_attrs = _make_fields_versionable(_get_fields(model))
    
    version_attrs.update({'__module__': model.__module__,
                      'Meta':Meta,
                      'versioned_id': m.IntegerField(),
                      'version_number': m.IntegerField(),
                      'change_time': m.DateTimeField(auto_now_add=True),
                      'change_type': m.TextField(),
                      })
                      
        
    return type(model.__name__+"Version",(m.Model,),version_attrs)


def _decorate_model(model,version_model):
    """
    Add versioning methods and attributes to the model
    """ 
    
    # Override __getattr__ to simulate having a foreign relation to 
    # the version model named 'versions'.  This may also be possible using a custom
    # manager, but seems more complicated since the instance id is required.  A regular
    # FK could not be used since it places constraints preventing deleting the versioned object
    
    # assert 'versions' not in model.__dict__.keys()
    # Add to the model's __getattr__ function so that versinos are handled properly
    try:
        old_getattr = model.__getattr__
    except AttributeError:
        old_getattr = None
    
    def _getattr(self, name):
        if name == 'versions':
            return version_model.objects.filter(versioned_id=self.id)
        else:
            if old_getattr <> None:
                return old_getattr(self,name)
            else: raise AttributeError, name
                 
    model.__getattr__ = _getattr
    
    
    def __unicode__(self):
        return u'Version %d' % (self.version_number)
    
    
    #assert 'get_latest_version' not in model.__dict__.keys()
    if 'get_latest_version' not in model.__dict__.keys():
        #print "adding get latest version"
        def get_latest_version(self):
            try:        
                latest_version = self.versions.order_by('-version_number')[0].version_number
            except IndexError:
                latest_version = 0 
            return latest_version
        setattr(model,'get_latest_version',get_latest_version)
    
    
    #assert 'revert' not in model.__dict__.keys()
    if 'revert' not in model.__dict__.keys():
        #print "adding revert"
        def revert(self,version=-1):
            """
            NOTE: latest version may refer to a later version of the object
                    if the object has been reverted but not saved
            
            Reverts a versioned model back to the specified version.
            If target_version is negative, go back that many versions
            Minimum version is 1, anythin earlier just revert to first version
            If requested version is greater than current version, do nothing
            """
            latest_version = self.get_latest_version()       
            
            # If no versions yet, do nothing. If version to high, revert to latest
            if latest_version < 1:
                return True
            if version >= latest_version:
                self.revert(latest_version)
                return True
            
            # If negative version, go back that many versions
            if version < 0:
                target_version = latest_version + version
            else:
                target_version = version
            
            # If version earlier than 1, return first version
            if target_version < 1:
                version_instance = self.versions.get(version_number__exact=1)
            else:
                version_instance = self.versions.get(version_number__exact=target_version)
            
            # Copy attribtues from version instance to object
            _rebuild_from_version(version_instance,self)
            return True       
        setattr(model,'revert',revert)    
    

def _copy_instance_vals(source_instance,target_instance):    
    """
    Copies all non-pk field values from source to target
    by checking which fields from source are also in target
    """
    for attr in _get_fields(source_instance).keys():
        if attr in _get_fields(target_instance.__class__).keys():
            if isinstance(source_instance._meta.get_field(attr),RelatedField):
                # Just copy the value of the PK pointed to by the FK
                pk_attr = source_instance._meta.get_field(attr).get_attname()
                value = getattr(source_instance,pk_attr)
            else: 
                value = source_instance._meta.get_field(attr).value_from_object(source_instance)
            setattr(target_instance,attr,value)
            

def _version_from_instance(model_instance,version_model):
    """
    Converts from an instance of model to an instance of version_model
    by copying over shared field values and setting the relation
    """
    version_instance = version_model()    
    _copy_instance_vals(model_instance,version_instance)    
    version_instance.version_number = model_instance.get_latest_version() + 1    
    version_instance.versioned_id = model_instance.id
    return version_instance

def _rebuild_from_version(version_instance,model_instance):
    """
    Populates the fields of a model instance based on versioned data. 
    Need to be carefull of fields that are an FK in the model since only
    the pk of the related object will have been versioned.
    
    For relation fields, we need to consider the possibility that the related object
    has been deleted and is not availabel, in that case set the relation to None
    """
    # Loop through the model's fields
    for field in _get_fields(model_instance).values():
        if field.name not in _get_fields(version_instance).keys():
            continue
        
        if isinstance(field,RelatedField):
            # The field is a Relation, get the pk value from the versioned data and 
            # try to get the related object, 
            rel_pk = getattr(version_instance,field.name)
            related_type = model_instance._meta.get_field(field.name).rel.to
            try:
                value = related_type.objects.get(pk=rel_pk)
            except ObjectDoesNotExist:
                value = None            
            setattr(model_instance,field.name,value)
        else:
            setattr(model_instance,field.name,getattr(version_instance,field.name))        
