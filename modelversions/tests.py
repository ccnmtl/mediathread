"""
#For questions or coments, please contact Robin Percy, rpercy at gmail dot com
# Start doctests

# Create instances
>>> m_one_1 = ModelOne(name='foo')
>>> m_one_2 = ModelOne(name='bar')
>>> m_two_1 = ModelTwo(name='franz',num=11)
>>> print m_one_1.testattr
Called __getattr__

# Versions should be created on each save
>>> m_one_1.save()
>>> m_one_1.name='foo2'
>>> m_one_1.save()
>>> m_one_1.versions.count()
2

>>> m_two_1.save()
>>> m_two_1.name='billie'
>>> m_two_1.num=22
>>> m_two_1.save()
>>> m_two_1.name='suzie'
>>> m_two_1.num=33
>>> m_two_1.save()
>>> m_two_1.versions.count()
3

# Test reverting
# By default, reverts back 1
>>> m_one_1.name
'foo2'
>>> m_one_1.revert()
True
>>> m_one_1.name
'foo'

# Can specify version to revert to
>>> m_two_1.name
'suzie'
>>> m_two_1.num
33
>>> m_two_1.revert(1)
True
>>> m_two_1.name
'franz'
>>> assert m_two_1.num == 11

# Use negative versions to revert number of steps backward from latest
>>> m_two_1.revert(-1)
True
>>> m_two_1.name
'billie'
>>> m_two_1.num
22

# If no stored versions yet, reverting does nothing
>>> m_one_2.revert()
True
>>> m_one_2.name
'bar'

# Use undelete to resurrect deleted objects
>>> id = m_one_1.id
>>> m_one_1.delete()
>>> from django.core.exceptions import ObjectDoesNotExist
>>> try:
...     ModelOne.objects.get(id=m_one_1.id)
... except ObjectDoesNotExist, e:
...     print "DELETED"
DELETED
>>> from djangotest.modelversions import undelete
>>> res = undelete(ModelOne,id)
>>> res.name
'foo'


# FK constraints should not be copied to versions.  So they should work normally
>>> p = TestParent(name='parent')
>>> c = TestChild(name='child')

>>> p.save()
>>> c.parent=p
>>> c.save()
>>> c.parent.name
'parent'
>>> p2 = TestParent(name='new_parent')
>>> p2.save()
>>> c.parent = p2
>>> c.save()
>>> c.parent.name
'new_parent'
>>> c.revert()
True
>>> c.parent.name
'parent'

#Test Many To Many Field
>>> many = ManyTest(name='manytest')
>>> many.save()
>>> many.subs.count()
0L
>>> m1 = ModelOne(name='one')
>>> m1.save()
>>> m2 = ModelOne(name='two')
>>> m2.save()
>>> m3 = ModelOne(name='three')
>>> m3.save()
>>> many.subs.add(m1)
>>> many.subs.add(m2)
>>> many.subs.add(m3)
>>> many.save()
>>> many.subs.count()
3L
>>> many.revert()
True
>>> many.subs.count()
3L

"""
from django.db import models
from djangotest.modelversions import version_model

# Dummy models to test versioning
class ModelOne(models.Model):
    name = models.CharField(maxlength=25)
    time = models.DateTimeField(auto_now_add=True)
    
    def __getattr__(self,name):
        if name == 'testattr':
            return "Called __getattr__"
        else: raise AttributeError, name
        
ModelOneVersion = version_model(ModelOne)

class ModelTwo(models.Model):
    name = models.CharField(maxlength=25)
    num = models.IntegerField()
ModelTwoVersion = version_model(ModelTwo)

class TestParent(models.Model):
    name = models.CharField(maxlength=25)
TestParentVersion = version_model(TestParent)

class TestChild(models.Model):
    name = models.CharField(maxlength=25)
    parent = models.ForeignKey(TestParent)
TestChildVersion = version_model(TestChild)

class ManyTest(models.Model):
    name = models.CharField(maxlength=25)
    subs = models.ManyToManyField(ModelOne)
ManyTestVersion = version_model(ManyTest)