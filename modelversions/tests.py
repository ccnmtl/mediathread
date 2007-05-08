"""
#For questions or coments, please contact Robin Percy, rpercy at gmail dot com
# Start doctests

# Create instances
>>> m_one_1 = ModelOne(name='foo')
>>> m_one_2 = ModelOne(name='bar')
>>> m_two_1 = ModelTwo(name='franz',num=11)

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

"""
from django.db import models
from djangotest.modelversions import version_model

# Dummy models to test versioning
class ModelOne(models.Model):
    name = models.CharField(maxlength=25)
    time = models.DateTimeField(auto_now_add=True)
ModelOneVersion = version_model(ModelOne)

class ModelTwo(models.Model):
    name = models.CharField(maxlength=25)
    num = models.IntegerField()
ModelTwoVersion = version_model(ModelTwo)