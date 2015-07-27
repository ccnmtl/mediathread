from datetime import datetime
from django.db import models
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q
from structuredcollaboration.models import Collaboration
from threadedcomments.models import ThreadedComment


PROJECT_TYPES = (
    ('Assignment', 'assignment'),
    ('Composition', 'composition')
)

PUBLISH_OPTIONS = (
    ('PrivateEditorsAreOwners', 'Private - only author(s) can view'),

    ('InstructorShared',
     'Instructor - only author(s) and instructor can view'),

    ('CourseProtected', 'Whole Class - all class members can view'),

    ('PublicEditorsAreOwners', 'Whole World - a public url is provided'),
)

SHORT_NAME = {
    'PrivateEditorsAreOwners': 'Private',
    'InstructorShared': 'Submitted to Instructor',
    'CourseProtected': 'Published to Class',
    'PublicEditorsAreOwners': 'Published to World',
    'PrivateStudentAndFaculty': 'with Instructors',
}

PUBLISH_OPTIONS_STUDENT_COMPOSITION = ['PrivateEditorsAreOwners',
                                       'InstructorShared',
                                       'CourseProtected']

PUBLISH_OPTIONS_STUDENT_ASSIGNMENT = ['PrivateEditorsAreOwners',
                                      'InstructorShared',
                                      'CourseProtected']

PUBLISH_OPTIONS_FACULTY = ['PrivateEditorsAreOwners',
                           'CourseProtected']

PUBLISH_OPTIONS_PUBLIC = ('PublicEditorsAreOwners',
                          'Whole World - a public url is provided')


class ProjectManager(models.Manager):

    def migrate(self, project_set, course, user, object_map,
                include_tags, include_notes):
        note_model = models.get_model('djangosherd', 'sherdnote')
        asset_model = models.get_model('assetmgr', 'asset')

        for old_project in project_set:
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
                        new_note = note_model.objects.migrate_one(
                            old_note, new_asset, user,
                            include_tags, include_notes)

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
        new_project = Project.objects.create(title=project.title,
                                             project_type=project.project_type,
                                             course=course,
                                             author=user)

        collaboration_context = Collaboration.objects.get_for_object(course)

        policy_record = project.get_collaboration().policy_record

        Collaboration.objects.create(
            user=new_project.author, title=new_project.title,
            content_object=new_project,
            context=collaboration_context,
            policy_record=policy_record)

        return new_project

    def visible_by_course(self, course, user):
        projects = Project.objects.filter(course=course)
        projects = projects.order_by('-modified', 'title')
        return [p for p in projects if p.visible(course, user)]

    def visible_by_course_and_user(self, course, viewer, user, is_faculty):
        projects = Project.objects.filter(
            Q(author=user, course=course) |
            Q(participants=user, course=course)
        ).distinct()

        lst = [p for p in projects if p.visible(course, viewer)]
        lst.sort(reverse=False, key=lambda project: project.title)
        lst.sort(reverse=True, key=lambda project: project.modified)

        if not is_faculty:
            lst.sort(reverse=True,
                     key=lambda project: project.feedback_date() or
                     project.modified)
        return lst

    def by_course_and_users(self, course, user_ids):
        projects = Project.objects.filter(
            Q(author__id__in=user_ids, course=course) |
            Q(participants__id__in=user_ids, course=course)).distinct()

        return projects.order_by('-modified', 'title')

    def faculty_compositions(self, course, user):
        projects = []
        prof_projects = Project.objects.filter(
            course.faculty_filter).order_by('ordinality', 'title')
        for project in prof_projects:
            if (project.class_visible() and
                    not project.is_assignment()):
                projects.append(project)

        return projects

    def unresponded_assignments(self, course, user):
        projects = list(Project.objects.filter(course.faculty_filter,
                                               due_date__isnull=False).
                        order_by("due_date", "-modified", "title"))

        projects.extend(Project.objects.filter(course.faculty_filter,
                                               due_date__isnull=True).
                        order_by("-modified", "title"))

        assignments = []
        project_type = ContentType.objects.get_for_model(Project)

        for assignment in projects:
            if (assignment.visible(course, user) and
                assignment.is_unanswered_assignment(course,
                                                    user,
                                                    project_type)):
                assignments.append(assignment)

        return assignments

    def reset_publish_to_world(self, course):
        # Check any existing projects -- if they are
        # world publish-able, turn this feature OFF
        projects = Project.objects.filter(course=course)
        for project in projects:
            try:
                col = Collaboration.objects.get_for_object(project)
                if col.policy_record.policy_name == 'PublicEditorsAreOwners':
                    col.set_policy('CourseProtected')
                    col.save()
            except:
                pass


class Project(models.Model):
    objects = ProjectManager()  # custom manager

    title = models.CharField(max_length=1024)

    course = models.ForeignKey(Course, related_name='project_set')

    # this is actually the LAST UPDATER for version-control purposes
    # (and wow does that make a mess of things!)
    author = models.ForeignKey(User)

    participants = models.ManyToManyField(User,
                                          null=True,
                                          blank=True,
                                          related_name='projects',
                                          verbose_name='Authors',)

    # modelversions attributes
    only_save_if_changed = True
    only_save_version_if_changed_fields_to_ignore = ['modified', 'author']

    body = models.TextField(blank=True)

    # available to someone other than the authors
    # -- at least, the instructor, if not the whole class
    submitted = models.BooleanField(default=False)

    modified = models.DateTimeField('date modified',
                                    editable=False,
                                    auto_now=True)

    due_date = models.DateTimeField('due date',
                                    null=True,
                                    blank=True)

    ordinality = models.IntegerField(default=-1)

    project_type = models.TextField(choices=PROJECT_TYPES,
                                    default='composition')

    def clean(self):
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
            col = self.get_collaboration()
        if col and col.policy_record.policy_name == 'PublicEditorsAreOwners':
            return col.get_absolute_url()

    def subobjects(self, course, viewer, child_type):
        col = self.get_collaboration()
        if not col:
            return []
        children = col.children.filter(content_type=child_type)
        viewable_children = []
        for child in children:
            if (child.permission_to("read", course, viewer) and
                    child.content_object):
                viewable_children.append(child.content_object)
        return viewable_children

    def discussions(self, course, viewer):
        discussion_type = ContentType.objects.get_for_model(ThreadedComment)
        return self.subobjects(course, viewer, discussion_type)

    def responses(self, course, viewer):
        project_type = ContentType.objects.get_for_model(Project)
        return self.subobjects(course, viewer, project_type)

    def responses_by(self, course, viewer, by_user):
        responses = self.responses(course, viewer)
        return [response for response in responses
                if (by_user in response.content_object.participants.all() or
                    by_user == response.content_object.author)]

    def description(self):
        if self.assignment():
            return "Assignment Response"
        elif self.is_assignment():
            return "Assignment"
        else:
            return "Composition"

    def is_assignment(self):
        return self.project_type == 'assignment'

    def assignment(self):
        """
        Returns the Project object that this Project is a response to,
        or None if this Project is not a response to any other.
        """
        col = self.get_collaboration()
        if col:
            parent = col.get_parent()
            if parent:
                return parent.content_object

        return None

    def is_unanswered_assignment(self, course, user, expected_type):
        """
        Returns True if this user has a response to this project
        or None if this user has not yet created a response
        """
        if not self.is_assignment():
            return False

        children = self.get_collaboration().children.all()
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
         professor feedback (assuming it's private)'''
        thread = None
        col = self.get_collaboration()
        if col:
            comm_type = ContentType.objects.get_for_model(ThreadedComment)

            feedback = col.children.filter(content_type=comm_type)
            if feedback:
                thread = feedback[0].content_object

        return thread

    def visibility(self):
        opts = dict(PUBLISH_OPTIONS)

        col = self.get_collaboration()
        if col:
            return opts.get(col.policy_record.policy_name,
                            col.policy_record.policy_name)
        elif self.submitted:
            return u"Submitted"
        else:
            return u"Private"

    def visibility_short(self):
        col = self.get_collaboration()
        if col:
            return SHORT_NAME.get(col.policy_record.policy_name,
                                  col.policy_record.policy_name)
        elif self.submitted:
            return u"Submitted"
        else:
            return u"Private"

    def status(self):
        col = self.get_collaboration()
        if col:
            status = SHORT_NAME.get(col.policy_record.policy_name,
                                    col.policy_record.policy_name)
            public_url = self.public_url(col)
            if public_url:
                status += ' (<a href="%s">public url</a>)' % public_url
            return status
        elif self.submitted:
            return u"Submitted"
        else:
            return u"Private"

    def is_participant(self, user):
        return (user == self.author or user in self.participants.all())

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
        col = self.get_collaboration()
        if not col:
            # legacy
            return self.submitted

        return (col.policy_record.policy_name != 'PrivateEditorsAreOwners' and
                col.policy_record.policy_name != 'InstructorShared')

    def visible(self, course, user):
        col = self.get_collaboration()
        if col:
            return col.permission_to('read', course, user)
        else:
            return self.submitted

    def can_edit(self, course, user):
        if not self.is_participant(user):
            return False
        col = self.get_collaboration()
        return (col.permission_to('edit', course, user))

    def can_read(self, course, user):
        col = self.get_collaboration()
        return (col.permission_to('read', course, user))

    def collaboration_sync_group(self, collab):
        participants = self.participants.all()

        collab_group = collab.get_or_create_group()

        existing_members = set(collab_group.user_set.all())
        for user in participants:
            if user in existing_members:
                existing_members.discard(user)  # already accounted for
            else:
                collab_group.user_set.add(user)  # add new members

        # remaining members should be removed
        for ex_member in existing_members:
            collab_group.user_set.remove(ex_member)

    def create_or_update_collaboration(self, policy_name):
        try:
            col = Collaboration.objects.get_for_object(self)
            col.title = self.title
        except Collaboration.DoesNotExist:
            context = Collaboration.objects.get_for_object(self.course)
            col = Collaboration(user=self.author, title=self.title,
                                content_object=self, context=context)
        col.set_policy(policy_name)
        col.save()

        self.collaboration_sync_group(col)
        return col

    def get_collaboration(self):
        try:
            return Collaboration.objects.get_for_object(self)
        except Collaboration.DoesNotExist:
            return None

    def submitted_date(self):
        dt = None
        if self.submitted:
            versions = self.versions.filter(submitted=True)
            versions = versions.order_by('change_time')
            if versions.count() > 0:
                dt = versions[0].change_time
        return dt

    def feedback_date(self):
        thread = self.feedback_discussion()
        return thread.submit_date if thread else None
