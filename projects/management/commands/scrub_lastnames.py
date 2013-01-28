from django.core.management.base import BaseCommand
from projects.models import Project
from django.contrib.auth.models import User
import re


class Command(BaseCommand):
    args = ''
    help = 'Removes last names from all users \
            in the system and in Project titles'

    def handle(self, *args, **options):
        for project in Project.objects.all():
            if re.match(r"(\w+) \w+'s Project", project.title):
                project.title = re.sub(r"(\w+) \w+'s Project",
                                       r"\1's Project",
                                       project.title)
                project.save()
                print project.title
            elif (project.author.last_name and
                    project.title.find(project.author.last_name) >= 0):

                project.title = project.title.replace(project.author.last_name,
                                                      'XX')
                project.save()
                print project.title.replace(
                    'XX', '[%s --> XX]' % project.author.last_name)

        for user in User.objects.all():
            user.last_name = ''
            user.save()

        print 'Success: removed last names from accounts and project titles'
