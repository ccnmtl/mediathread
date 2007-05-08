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
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist

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
        version_instance.save()    

    def record_save(sender,instance,signal, *args, **kwargs):
        # Record the save to the shadow table
        record_change(instance,"SAVE")
    dispatcher.connect(record_save,signal=signals.post_save,sender=model,weak=False)
        
    def record_delete(sender,instance,signal,*args,**kwargs):
        # Record the delete to the shadow table
        record_change(instance,"DELETE")      
    dispatcher.connect(record_delete,signal=signals.pre_delete,sender=model,weak=False)     

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
        _copy_field_vals(version,instance)
        return instance
    except ObjectDoesNotExist,KeyError:
        return None
    


def _get_fields(model):
    """
    Returns a dict of field names and field objects for the model, excluding the pk field
    """
    return dict([ (field.name,field) for field in model._meta.fields if field.name != model._meta.pk.attname])


def _build_version_model(model):
    """
    Create a Shadow Model to store versioning info of model records
    """
    class Meta:        
        pass
        
    version_attrs = _get_fields(model)   
    version_attrs.update({'__module__': model.__module__,
                      'Meta':Meta,
                      'versioned_id': m.IntegerField(),
                      'version_number': m.IntegerField(),
                      'change_time': m.DateTimeField(auto_now_add=True),
                      'change_type': m.CharField(maxlength=10),})    
        
    return type(model.__name__+"Version",(m.Model,),version_attrs)


def _decorate_model(model,version_model):
    """
    Add versioning methods and attributes to the model
    """ 
    
    # Override __getattr__ to simulate having a foreign relation to 
    # the version model named 'versions'.  This may also be possible using a custom
    # manager, but seems more complicated since the instance id is required.  A regular
    # FK could not be used since it places constraints preventing deleting the versioned object
    
    assert '__getattr__' not in model.__dict__.keys()    
    def _getattr(self, name):
        if name == 'versions':
            return version_model.objects.filter(versioned_id=self.id)
        else:  raise AttributeError, name    
    model.__getattr__ = _getattr
    
    assert 'get_latest_version' not in model.__dict__.keys()
    def get_latest_version(self):
        try:        
            latest_version = self.versions.order_by('-version_number')[0].version_number
        except IndexError:
            latest_version = 0 
        return latest_version
    setattr(model,'get_latest_version',get_latest_version)
    
    assert 'revert' not in model.__dict__.keys()
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
        _copy_field_vals(version_instance,self)
        return True       
    setattr(model,'revert',revert)
    

def _copy_field_vals(source_instance,target_instance):    
    """
    Copies all non-pk field values from source to target
    by checking which fields from source are also in target
    """
    for attr in source_instance.__dict__.keys():
        if attr in _get_fields(target_instance.__class__).keys():
            setattr(target_instance,attr,source_instance.__dict__[attr])
            

def _version_from_instance(model_instance,version_model):
    """
    Converts from an instance of model to an instance of version_model
    by copying over shared field values and setting the relation
    """
    version_instance = version_model()    
    _copy_field_vals(model_instance,version_instance)    
    version_instance.version_number = model_instance.get_latest_version() + 1    
    version_instance.versioned_id = model_instance.id
    return version_instance
