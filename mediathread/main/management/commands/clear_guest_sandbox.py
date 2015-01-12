from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from threadedcomments.models import ThreadedComment

from mediathread.assetmgr.models import Asset
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import SherdNote
from mediathread.main.course_details import get_guest_sandbox
from mediathread.projects.models import Project


class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        # kill assets & projects & comments not owned by sandbox_instructor
        sandbox = get_guest_sandbox()
        instructor = User.objects.get(username='sandbox_instructor')

        assets = Asset.objects.filter(course=sandbox)
        assets = assets.exclude(author=instructor)
        assets.delete()

        notes = SherdNote.objects.filter(asset__course=sandbox)
        notes = notes.exclude(author=instructor)
        notes.delete()

        projects = Project.objects.filter(course=sandbox)
        projects = projects.exclude(author=instructor)
        projects.delete()

        discussions = get_course_discussions(sandbox)
        parents = [d.id for d in discussions]
        comments = ThreadedComment.objects.filter(parent_id__in=parents)
        comments.delete()
