from django.db import models

STUDENT_AMOUNT_CHOICES = (
        (10, '1-9'),
        (20, '10-19'),
        (50, '20-49'),
        (100, '50-99'),
        (500, '100+')
        )
# Create your models here.

class CourseInformation(models.Model):
    student_amount = models.IntegerField(choices=STUDENT_AMOUNT_CHOICES)
    organization = models.ForeignKey('user_accounts.OrganizationModel')
    course = models.ForeignKey('courseaffils.Course')

    def __unicode__(self):
        if self.course:
            return self.course.title
        else:
            return "Unknown Course"


