from courseaffils.models import Course
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from structuredcollaboration.models import Collaboration
from threadedcomments.models import ThreadedComment


PUBLISH_OPTIONS = (
    ('PrivateEditorsAreOwners', 'Private - only author(s) can view'),

    ('InstructorShared',
     'Instructor - only author(s) and instructor can view'),

    ('CourseProtected', 'Whole Class - all class members can view'),

    ('Assignment',
     'Assignment - published to all students in class, tracks responses'),

    ('PublicEditorsAreOwners', 'Whole World - a public url is provided'),
)

SHORT_NAME = {
    "Assignment": 'Assignment',
    "PrivateEditorsAreOwners": 'Private',
    "InstructorShared": 'Submitted to Instructor',
    "CourseProtected": 'Published to Class',
    "PublicEditorsAreOwners": 'Published to World',
    "PrivateStudentAndFaculty": "with Instructors",
}

PUBLISH_OPTIONS_STUDENT_COMPOSITION = ['PrivateEditorsAreOwners',
                                       'InstructorShared',
                                       'CourseProtected']

PUBLISH_OPTIONS_STUDENT_ASSIGNMENT = ['PrivateEditorsAreOwners',
                                      'InstructorShared',
                                      'CourseProtected']

PUBLISH_OPTIONS_FACULTY = ['PrivateEditorsAreOwners',
                           'Assignment',
                           'CourseProtected']

PUBLISH_OPTIONS_PUBLIC = ('PublicEditorsAreOwners',
                          'Whole World - a public url is provided')


class ProjectManager(models.Manager):

    def migrate(self, project_set, course, user, object_map):
        note_model = models.get_model('djangosherd', 'sherdnote')
        asset_model = models.get_model('assetmgr', 'asset')

        for project_json in project_set:
            old_project = Project.objects.get(id=project_json['id'])
            project_body = old_project.body
            citations = note_model.objects.references_in_string(project_body,
                                                                user)

            new_project = Project.objects.migrate_one(old_project,
                                                      course,
                                                      user)

            for old_note in citations:
                new_note = None
                new_asset = None
                try:
                    if old_note.id in object_map['notes']:
                        new_note = object_map['notes'][old_note.id]
                    else:
                        if old_note.asset.id in object_map['assets']:
                            new_asset = object_map['assets'][old_note.asset.id]
                        else:
                            # migrate the asset
                            new_asset = asset_model.objects.migrate_one(
                                old_note.asset, course, user)
                            object_map['assets'][old_note.asset.id] = new_asset

                        # migrate the note
                        new_note = note_model.objects.migrate_one(old_note,
                                                                  new_asset,
                                                                  user)

                        object_map['notes'][old_note.id] = new_note

                    # Update the citations in the body with the new id(s)
                    project_body = \
                        new_note.update_references_in_string(
                            project_body, old_note)

                    project_body = \
                        new_note.asset.update_references_in_string(
                            project_body, old_note.asset)
                except asset_model.DoesNotExist:
                    # todo: The asset was deleted, but is still referenced.
                    pass

            new_project.body = project_body
            new_project.save()
            object_map['projects'][old_project.id] = new_project

        return object_map

    def migrate_one(self, project, course, user):
        new_project = Project(title=project.title,
                              course=course,
                              author=user)
        new_project.save()

        collaboration_context = Collaboration.objects.get(
            content_type=ContentType.objects.get_for_model(Course),
            object_pk=str(course.pk))

        policy = project.collaboration()._policy

        Collaboration.objects.create(
            user=new_project.author, title=new_project.title,
            content_object=new_project,
            context=collaboration_context, policy=policy.policy_name)

        return new_project

    def visible_by_course(self, request, course):
        projects = Project.objects.filter(course=course)
        projects = projects.order_by('-modified', 'title')
        return [p for p in projects if p.visible(request)]

    def visible_by_course_and_user(self, request, course, user):
        projects = Project.objects.filter(Q(author=user, course=course)
                                          | Q(participants=user, course=course)
                                          ).distinct()

        projects = projects.order_by('-modified', 'title')
        return [p for p in projects if p.visible(request)]

    def unresponded_assignments(self, request, user):
        course = request.course
        projects = list(Project.objects.filter(course.faculty_filter,
                                               due_date__isnull=False).
                        order_by("due_date", "-modified", "title"))

        projects.extend(Project.objects.filter(course.faculty_filter,
                                               due_date__isnull=True).
                        order_by("-modified", "title"))

        assignments = []
        project_type = ContentType.objects.get_for_model(Project)

        for assignment in projects:
            if (assignment.visible(request) and
                assignment.is_unanswered_assignment(request,
                                                    user,
                                                    project_type)):
                assignments.append(assignment)

        return assignments


class Project(models.Model):
    objects = ProjectManager()  # custom manager

    title = models.CharField(max_length=1024)

    course = models.ForeignKey(Course, related_name='project_set')

    # this is actually the LAST UPDATER for version-control purposes
    author = models.ForeignKey(User)

    # should be limited to course members
    # maybe just in the form:
    # http://collingrady.wordpress.com/2008/07/24/useful-form-tricks-in-django/
    participants = models.ManyToManyField(User,
                                          null=True,
                                          blank=True,
                                          related_name='projects',
                                          verbose_name='Authors',)

    only_save_if_changed = True
    only_save_version_if_changed_fields_to_ignore = ['modified', 'author']

    body = models.TextField(blank=True)

    # available to someone other than the authors
    # -- at least, the instructor, if not the whole class
    submitted = models.BooleanField(default=False)

    # DEPRECATED: do not use this field
    feedback = models.TextField(blank=True, null=True)

    modified = models.DateTimeField('date modified',
                                    editable=False,
                                    auto_now=True)

    due_date = models.DateTimeField('due date',
                                    null=True,
                                    blank=True)

    ordinality = models.IntegerField(default=-1)

    def clean(self):
        from django.core.exceptions import ValidationError

        today = datetime.today()
        this_day = datetime(today.year, today.month, today.day, 0, 0)
        if self.due_date is not None and self.due_date < this_day:
            msg = "%s is not valid for the Due Date field.\n" % \
                self.get_due_date()
            msg = msg + "The date cannot be in the past.\n"
            raise ValidationError(msg)

    @models.permalink
    def get_absolute_url(self):
        return ('project-workspace', (), {'project_id': self.pk})

    def get_due_date(self):
        if self.due_date is None:
            return ""
        else:
            return self.due_date.strftime("%m/%d/%y")

    def public_url(self, col=None):
        if col is None:
            col = self.collaboration()
        if col and col._policy.policy_name == 'PublicEditorsAreOwners':
            return col.get_absolute_url()

    def subobjects(self, request, child_type):
        col = self.collaboration()
        if not col:
            return []
        children = col.children.filter(content_type=child_type)
        viewable_children = []
        for child in children:
            if child.permission_to("read", request) and child.content_object:
                viewable_children.append(child.content_object)
        return viewable_children

    def discussions(self, request):
        discussion_type = ContentType.objects.get_for_model(ThreadedComment)
        return self.subobjects(request, discussion_type)

    def responses_by(self, request, user):
        responses = self.responses(request)
        return [response for response in responses
                if response and
                (user in response.content_object.participants.all() or
                 user == response.content_object.author)]

    def responses(self, request):
        project_type = ContentType.objects.get_for_model(Project)
        return self.subobjects(request, project_type)

    def description(self):
        if self.assignment():
            return "Assignment Response"
        elif self.visibility_short() == "Assignment":
            return "Assignment"
        else:
            return "Composition"

    def is_assignment(self, request):
        if hasattr(self, 'is_assignment_cached'):
            return self.is_assignment_cached
        col = self.collaboration()
        if not col:
            return False
        self.is_assignment_cached = col.permission_to("add_child", request)
        return self.is_assignment_cached

    def assignment(self):
        """
        Returns the Project object that this Project is a response to,
        or None if this Project is not a response to any other.
        """
        # TODO: this doesn't check content types in any way.
        # It assumes that obj->collab->parent->obj is-a Project.
        col = self.collaboration()
        if not col:
            return
        parent = col.get_parent()
        if not parent:
            return
        return parent.content_object

    def is_unanswered_assignment(self, request, user, expected_type):
        """
        Returns True if this user has a response to this project
        or None if this user has not yet created a response
        """
        if not self.is_assignment(request):
            return False

        collab = self.collaboration()
        children = collab.children.all()
        if not children:
            # It has no responses, but it looks like an assignment
            return True

        for child in children:
            if child.content_type != expected_type:
                # Ignore this child, it isn't a project
                continue
            if getattr(child.content_object, 'author', None) == user:
                # Aha! We've answered it already
                return False

        # We are an assignment; we have children;
        # we haven't found a response by the target user.
        return True

    def feedback_discussion(self):
        '''returns the ThreadedComment object for
         Professor feedback (assuming it's private)'''
        col = self.collaboration()
        if not col:
            return
        comm_type = ContentType.objects.get_for_model(ThreadedComment)

        feedback = col.children.filter(content_type=comm_type)
        if feedback:
            return feedback[0].content_object

    def save(self, *args, **kw):
        models.Model.save(self)
        self.participants.add(self.author)
        self.collaboration(sync_group=True)

    def visibility(self):
        """
        The project's status, one of "draft submitted complete".split()
        """
        opts = dict(PUBLISH_OPTIONS)

        col = self.collaboration()
        if col:
            return opts.get(col._policy.policy_name, col._policy.policy_name)
        elif self.submitted:
            return u"Submitted"
        else:
            return u"Private"

    def visibility_short(self):
        col = self.collaboration()
        if col:
            return SHORT_NAME.get(col._policy.policy_name,
                                  col._policy.policy_name)
        elif self.submitted:
            return u"Submitted"
        else:
            return u"Private"

    def status(self):
        """
        The project's status, one of "draft submitted complete".split()
        """
        col = self.collaboration()
        if col:
            status = SHORT_NAME.get(col._policy.policy_name,
                                    col._policy.policy_name)
            public_url = self.public_url(col)
            if public_url:
                status += ' (<a href="%s">public url</a>)' % public_url
            return status
        elif self.submitted:
            return u"Submitted"
        else:
            return u"Private"

    def is_participant(self, user_or_request):
        user = getattr(user_or_request, 'user', user_or_request)
        return (user == self.author
                or user in self.participants.all())

    def citations(self):
        """
        citation references to sherdnotes
        """
        note_model = models.get_model('djangosherd', 'SherdNote')
        return note_model.objects.references_in_string(self.body, self.author)

    @property
    def content_object(self):
        """Support similar property as Comment model"""
        return self

    def attribution_list(self):
        participants = list(self.participants.all())
        if self.author not in participants:
            participants.insert(0, self.author)
        return participants

    def attribution(self, participants=None):
        participants = self.attribution_list()
        return ', '.join([p.get_full_name() or p.username
                          for p in participants])

    def __unicode__(self):
        return u'%s <%r> by %s' % (self.title, self.pk, self.attribution())

    def class_visible(self):
        col = self.collaboration()
        if not col:
            # legacy
            return self.submitted

        return (col._policy.policy_name != 'PrivateEditorsAreOwners'
                and col._policy.policy_name != 'InstructorShared')

    def visible(self, request):
        col = self.collaboration()
        if col:
            return col.permission_to('read', request)
        else:
            return self.submitted

    def can_edit(self, request):
        if not self.is_participant(request.user):
            return False

        return (self.collaboration(request).permission_to('edit', request) or
                self.collaboration(
                    request, sync_group=True).permission_to('edit', request))

    def can_read(self, request):
        return (self.collaboration(request).permission_to('read', request) or
                self.collaboration(
                    request, sync_group=True).permission_to('read', request))

    def collaboration(self, request=None, sync_group=False):
        col = None
        policy = None
        if request and request.method == "POST":
            policy = request.POST.get('publish', 'PrivateEditorsAreOwners')

        try:
            col = Collaboration.get_associated_collab(self)
        except Collaboration.DoesNotExist:
            if policy is None:
                policy = "PrivateEditorsAreOwners"

            if request is not None:
                col = Collaboration.objects.create(
                    user=self.author, title=self.title, content_object=self,
                    context=request.collaboration_context, policy=policy,)

        if col is None:  # iff collab did not exist and request is None
            return

        if sync_group:
            participants = self.participants.all()
            if (len(participants) > 1 or
                (col.group_id and col.group.user_set.count() > 1)
                    or (self.author not in participants and
                        len(participants) > 0)):
                colgrp = col.have_group()
                already_grp = set(colgrp.user_set.all())
                for user in participants:
                    if user in already_grp:
                        already_grp.discard(user)
                    else:
                        colgrp.user_set.add(user)
                for oldp in already_grp:
                    colgrp.user_set.remove(oldp)
            if request and request.method == "POST" and \
                    (col.policy != policy or col.title != self.title):
                col.title = self.title
                col.policy = policy
                col.save()

        return col

    def content_metrics(self):
        "Do some rough heuristics on how much each author contributed"
        last_content = ''
        author_contributions = {}
        for version in self.versions:
            change = len(version.body) - len(last_content)
            author_contributions.setdefault(version.author, [0, 0])
            if change > 0:  # track adds
                author_contributions[version.author][0] += change
            elif change < 0:  # track deletes
                author_contributions[version.author][1] -= change
            last_content = version.body
        return author_contributions


@receiver(post_save, sender=ThreadedComment)
def on_threaded_comment_save(sender, **kwargs):
    instance = kwargs['instance']
    while instance.parent is not None:
        instance = instance.parent

    an_object = instance.content_object._parent.content_object
    if hasattr(an_object, 'modified'):
        an_object.modified = datetime.now()
        an_object.save()
