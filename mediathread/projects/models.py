from datetime import datetime

from courseaffils.models import Course
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
import reversion
from threadedcomments.models import ThreadedComment

from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote
from mediathread.sequence.models import SequenceAsset
from mediathread.main.course_details import cached_course_is_faculty
from mediathread.main.util import user_display_name
from structuredcollaboration.models import Collaboration


PROJECT_TYPE_ASSIGNMENT = 'assignment'
PROJECT_TYPE_COMPOSITION = 'composition'
PROJECT_TYPE_SELECTION_ASSIGNMENT = 'selection-assignment'
PROJECT_TYPE_SEQUENCE_ASSIGNMENT = 'sequence-assignment'
PROJECT_TYPES = (
    (PROJECT_TYPE_ASSIGNMENT, 'Composition Assignment'),
    (PROJECT_TYPE_COMPOSITION, 'Composition'),
    (PROJECT_TYPE_SELECTION_ASSIGNMENT, 'Selection Assignment')
)

PUBLISH_DRAFT = ('PrivateEditorsAreOwners', 'Draft - only you can view')
PUBLISH_INSTRUCTOR_SHARED = \
    ('InstructorShared', 'Instructor - only author(s) and instructor can view')
PUBLISH_WHOLE_CLASS = \
    ('CourseProtected', 'Whole Class - all class members can view')
PUBLISH_WHOLE_WORLD = \
    ('PublicEditorsAreOwners', 'Whole World - a public url is provided')

SHORT_NAME = {
    'PrivateEditorsAreOwners': 'Draft',
    'InstructorShared': 'Submitted to Instructor',
    'CourseProtected': 'Published to Class',
    'PublicEditorsAreOwners': 'Published to World',
    'PrivateStudentAndFaculty': 'with Instructors',
}

PUBLISH_OPTIONS = dict([PUBLISH_DRAFT, PUBLISH_INSTRUCTOR_SHARED,
                        PUBLISH_WHOLE_CLASS, PUBLISH_WHOLE_WORLD])

RESPONSE_VIEW_NEVER = (
    'never', 'Never - Responses visible only to instructors')
RESPONSE_VIEW_SUBMITTED = (
    'submitted',
    'After Submission - Response required to view other student responses '
    'before due date. All responses visible after assignment due date passes.')
RESPONSE_VIEW_ALWAYS = (
    'always', 'Always - Response not required to view other student responses')
RESPONSE_VIEW_POLICY = (
    RESPONSE_VIEW_NEVER, RESPONSE_VIEW_ALWAYS, RESPONSE_VIEW_SUBMITTED)


class ProjectManager(models.Manager):

    def migrate(self, project_set, course, user, object_map,
                include_tags, include_notes):

        for old_project in project_set:
            project_body = old_project.body
            citations = SherdNote.objects.references_in_string(project_body,
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
                            new_asset = Asset.objects.migrate_one(
                                old_note.asset, course, user)
                            object_map['assets'][old_note.asset.id] = new_asset

                        # migrate the note
                        new_note = SherdNote.objects.migrate_one(
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
                except Asset.DoesNotExist:
                    # todo: The asset was deleted, but is still referenced.
                    pass

            new_project.body = project_body
            new_project.save()

            self.migrate_assignment_item(course, user,
                                         old_project, new_project, object_map)

            object_map['projects'][old_project.id] = new_project

        return object_map

    def migrate_one(self, project, course, user):
        new_project = Project.objects.create(
            title=project.title, project_type=project.project_type,
            course=course, author=user,
            response_view_policy=project.response_view_policy)

        collaboration_context = Collaboration.objects.get_for_object(course)

        policy_record = project.get_collaboration().policy_record

        Collaboration.objects.create(
            user=new_project.author, title=new_project.title,
            content_object=new_project,
            context=collaboration_context,
            policy_record=policy_record)

        return new_project

    def migrate_assignment_item(self, course, user,
                                old_project, new_project, object_map):
        aItem = AssignmentItem.objects.filter(project=old_project).first()
        if aItem is not None:
            if aItem.asset.id in object_map['assets']:
                new_asset = object_map['assets'][aItem.asset.id]
            else:
                # migrate the asset
                new_asset = Asset.objects.migrate_one(
                    aItem.asset, course, user)
                object_map['assets'][aItem.asset.id] = new_asset

            AssignmentItem.objects.create(project=new_project,
                                          asset=new_asset)

    def visible_by_course(self, course, viewer):
        projects = Project.objects.filter(course=course)

        visible = []
        for collab in Collaboration.objects.get_for_object_list(projects):
            project = collab.content_object
            if project.can_read(course, viewer, collab):
                visible.append(project)

        visible.sort(reverse=False, key=lambda project: project.title)
        visible.sort(reverse=True, key=lambda project: project.modified)
        return visible

    def visible_by_course_and_user(self, course, viewer, user, is_faculty):
        projects = Project.objects.filter(
            Q(author=user, course=course) |
            Q(participants=user, course=course)
        ).distinct()

        lst = []
        for collab in Collaboration.objects.get_for_object_list(projects):
            project = collab.content_object
            if project.can_read(course, viewer, collab):
                lst.append(project)

        lst.sort(reverse=False, key=lambda project: project.title)
        lst.sort(reverse=True, key=lambda project: project.modified)

        if not is_faculty:
            lst.sort(reverse=True,
                     key=lambda project: project.feedback_date() or
                     project.modified)
        return lst

    def responses_by_course(self, course, viewer):
        projects = Project.objects.filter(
            course=course, project_type=PROJECT_TYPE_COMPOSITION)

        # filter down to responses only based on the collaboration parent state
        collaborations = Collaboration.objects.get_for_object_list(projects)
        collaborations = collaborations.filter(_parent__isnull=False)
        collaborations = collaborations.order_by('object_pk')

        # get all the content objects at once
        ids = [int(c.object_pk) for c in collaborations]
        responses = Project.objects.filter(id__in=ids)
        responses = list(responses.select_related('author'))
        responses.sort(reverse=False, key=lambda p: str(p.id))

        visible = []
        hidden = []
        for idx, r in enumerate(responses):
            assert str(r.id) == collaborations[idx].object_pk
            if r.can_read(course, viewer, collaborations[idx]):
                visible.append(r)
            else:
                hidden.append(r)
        return visible, hidden

    def by_course_and_users(self, course, user_ids):
        projects = Project.objects.filter(
            Q(author__id__in=user_ids, course=course) |
            Q(participants__id__in=user_ids, course=course)).distinct()
        projects = projects.select_related('author')
        return projects.order_by('-modified', 'title')

    def faculty_compositions(self, course, user):
        qs = Project.objects.filter(
            course=course,
            author__in=course.faculty_group.user_set.all())
        qs = qs.select_related('author')
        qs = qs.filter(project_type=PROJECT_TYPE_COMPOSITION)

        # filter private compositions
        lst = Collaboration.objects.get_for_object_list(qs)
        lst = lst.exclude(policy_record__policy_name=PUBLISH_DRAFT[0])

        # get all the projects at once
        ids = [int(c.object_pk) for c in lst]
        return Project.objects.filter(id__in=ids).order_by('ordinality',
                                                           'title')

    def unresponded_assignments(self, course, user):
        qs = Project.objects.filter(
            course=course,
            author__in=course.faculty_group.user_set.all())
        qs = qs.exclude(project_type=PROJECT_TYPE_COMPOSITION)

        # filter private assignments
        lst = Collaboration.objects.get_for_object_list(qs)
        lst = lst.filter(policy_record__policy_name=PUBLISH_DRAFT[0])
        ids = [int(c.object_pk) for c in lst]
        qs = qs.exclude(id__in=ids)

        projects = list(qs.filter(due_date__isnull=False).
                        order_by("due_date", "-modified", "title"))

        projects.extend(qs.filter(due_date__isnull=True).
                        order_by("-modified", "title"))

        assignments = []

        for assignment in projects:
            responses = assignment.responses(course, user, user)
            if len(responses) < 1:
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

    def limit_response_policy(self, course):
        # Update response policy to be NEVER
        projects = Project.objects.filter(course=course)
        projects.update(response_view_policy=RESPONSE_VIEW_NEVER[0])


class Project(models.Model):
    """The Project model handles assignments and responses.

    A Project can be an assignment assigned by an instructor
    that can contain any number of responses (which are also
    Projects), created by the students.
    """
    DEFAULT_TITLE = 'Untitled'

    objects = ProjectManager()  # custom manager

    title = models.CharField(max_length=1024)

    course = models.ForeignKey(Course, related_name='project_set')

    # this is actually the LAST UPDATER for version-control purposes
    # (and wow does that make a mess of things!)
    author = models.ForeignKey(User)

    participants = models.ManyToManyField(User,
                                          blank=True,
                                          related_name='projects',
                                          verbose_name='Authors',)

    body = models.TextField(blank=True)

    custom_instructions_1 = models.CharField(
        max_length=140, null=True, blank=True)
    custom_instructions_2 = models.CharField(
        max_length=140, null=True, blank=True)

    date_submitted = models.DateTimeField(null=True, blank=True)

    modified = models.DateTimeField('date modified', editable=False,
                                    auto_now=True)

    due_date = models.DateTimeField('due date', null=True, blank=True)

    ordinality = models.IntegerField(default=-1)

    project_type = models.TextField(choices=PROJECT_TYPES,
                                    default=PROJECT_TYPE_COMPOSITION,
                                    db_index=True)

    response_view_policy = models.TextField(choices=RESPONSE_VIEW_POLICY,
                                            default='always')

    @models.permalink
    def get_absolute_url(self):
        return ('project-workspace', (), {'project_id': self.pk})

    def get_due_date(self):
        if self.due_date is None:
            return ""
        else:
            return self.due_date.strftime("%m/%d/%y")

    def is_empty(self):
        return self.title == self.DEFAULT_TITLE and len(self.body) == 0

    def public_url(self, col=None):
        if col is None:
            col = self.get_collaboration()
        if col and col.policy_record.policy_name == 'PublicEditorsAreOwners':
            return col.get_absolute_url()

    def _response_by_author(self, children, author):
        '''not protected by can_read, strictly internal'''
        children = children.filter(Q(user=author) | Q(group__user=author))
        response = children.first()
        if response:
            return response.content_object
        return None

    def responses(self, course, viewer, author=None):
        visible = []
        children = self.get_collaboration().get_children_for_object(
            self).prefetch_related('content_object__author')

        viewer_response = None
        if viewer and not viewer.is_anonymous():
            viewer_response = self._response_by_author(children, viewer)

        if author and not author.is_anonymous():
            children = children.filter(Q(user=author) | Q(group__user=author))

        for child in children:
            response = child.content_object
            if response.can_read(course, viewer, child, viewer_response):
                visible.append(response)
        return visible

    def description(self):
        if self.is_essay_assignment():
            return 'Composition Assignment'
        if self.is_selection_assignment():
            return 'Selection Assignment'
        if self.is_sequence_assignment():
            return 'Sequence Assignment'

        assignment = self.assignment()
        if not assignment:
            return 'Composition'

        if assignment.is_selection_assignment():
            return 'Selection Assignment Response'
        if assignment.is_sequence_assignment():
            return 'Sequence Assignment Response'

        return 'Composition Assignment Response'

    def is_assignment_type(self):
        return (self.is_essay_assignment() or self.is_selection_assignment() or
                self.is_sequence_assignment())

    def is_essay_assignment(self):
        return self.project_type == PROJECT_TYPE_ASSIGNMENT

    def is_selection_assignment(self):
        return self.project_type == PROJECT_TYPE_SELECTION_ASSIGNMENT

    def is_sequence_assignment(self):
        return self.project_type == PROJECT_TYPE_SEQUENCE_ASSIGNMENT

    def is_composition(self):
        return self.project_type == PROJECT_TYPE_COMPOSITION

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
        col = self.get_collaboration()
        if col:
            return PUBLISH_OPTIONS[col.policy_record.policy_name]
        else:
            return PUBLISH_DRAFT[0]

    def visibility_short(self):
        col = self.get_collaboration()
        if col:
            return SHORT_NAME.get(col.policy_record.policy_name,
                                  col.policy_record.policy_name)
        else:
            return PUBLISH_DRAFT[0]

    def status(self):
        col = self.get_collaboration()
        if col:
            status = SHORT_NAME.get(col.policy_record.policy_name,
                                    col.policy_record.policy_name)
            public_url = self.public_url(col)
            if public_url:
                status += ' (<a href="%s">public url</a>)' % public_url
            return status
        else:
            return u"Private"

    def is_participant(self, user):
        return (user == self.author or
                self.participants.filter(id=user.id).exists())

    def citations(self):
        """
        citation references to sherdnotes
        """
        return SherdNote.objects.references_in_string(self.body, self.author)

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
        return ', '.join([user_display_name(p) for p in participants])

    def __unicode__(self):
        return u'%s <%r> by %s' % (self.title, self.pk, self.attribution())

    def can_edit(self, course, user):
        if not self.is_participant(user):
            return False
        col = self.get_collaboration()
        return (col.permission_to('edit', course, user))

    def can_read(self, course, viewer,
                 the_collaboration=None, viewer_response=None):
        # has the author published his work?
        collaboration = the_collaboration or self.get_collaboration()
        if (collaboration is None) or \
           (not collaboration.permission_to('read', course, viewer)):
            return False

        # If this project is an assignment response, verify the parent
        # assignment's response policy sanctions a read by the viewer
        if (not self.is_composition() or
            collaboration.policy_record.policy_name ==
                PUBLISH_WHOLE_WORLD[0]):
            return True  # this project is an assignment

        parent = collaboration.get_parent()
        if parent is None:
            return True  # this project does not have a parent assignment

        # the author & faculty can always view a submitted response
        if (cached_course_is_faculty(course, viewer) or
                self.is_participant(viewer)):
            return True

        assignment = parent.content_object
        if (assignment.response_view_policy == RESPONSE_VIEW_ALWAYS[0]):
            return True
        elif assignment.response_view_policy == RESPONSE_VIEW_SUBMITTED[0]:
            viewer_response = (
                viewer_response or
                self._response_by_author(parent.get_children_for_object(self),
                                         viewer))
            return viewer_response and viewer_response.is_submitted()
        else:  # assignment.response_view_policy == 'never':
            return False

    def can_cite(self, course, viewer):
        # for selection assignment responses only

        # notes in an unsubmitted project are not citable
        if not self.is_submitted():
            return False

        parent = self.assignment()

        if (not parent or
                parent.response_view_policy == RESPONSE_VIEW_ALWAYS[0]):
            return True

        if parent.response_view_policy == RESPONSE_VIEW_SUBMITTED[0]:
            if parent.due_date and parent.due_date < datetime.today():
                return True

            # a bit hacky and very SLOW
            # but should work unless we get collaborative
            # do the visible responses == students
            responses = parent.responses(course, viewer)
            return course.students.count() == len(responses)

        return False

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
            col = Collaboration(user=self.author, title=self.title,
                                content_object=self)
        if col.context is None:
            col.context = Collaboration.objects.get_for_object(self.course)
        col.set_policy(policy_name)
        col.save()

        self.collaboration_sync_group(col)
        return col

    def create_or_update_item(self, item_id):
        try:
            item = Asset.objects.get(id=item_id)
            if self.assignmentitem_set.filter(asset=item).count() == 0:
                AssignmentItem.objects.create(project=self, asset=item)
                self.assignmentitem_set.exclude(asset=item).delete()
        except Asset.DoesNotExist:
            pass  # optional parameter

    def set_parent(self, parent_id):
        try:
            parent = Project.objects.get(id=parent_id)
            parent.get_collaboration().append_child(self)
        except Project.DoesNotExist:
            pass

    def get_collaboration(self):
        try:
            return Collaboration.objects.get_for_object(self)
        except Collaboration.DoesNotExist:
            return None

    def is_submitted(self):
        return self.date_submitted is not None

    def feedback_date(self):
        thread = self.feedback_discussion()
        return thread.submit_date if thread else None

    def latest_version(self):
        try:
            version = reversion.get_for_object(self).get_unique().next()
            return version.revision_id
        except StopIteration:
            return None

    def versions(self):
        # all previous versions, latest versions first, duplicates removed
        return reversion.get_for_object(self).get_unique()


reversion.register(Project)


class AssignmentItem(models.Model):
    asset = models.ForeignKey(Asset)
    project = models.ForeignKey(Project)


class ProjectNote(models.Model):
    annotation = models.ForeignKey(SherdNote)
    project = models.ForeignKey(Project)


class ProjectSequenceAsset(models.Model):
    """This model connects the SequenceAsset to the Project."""
    sequence_asset = models.ForeignKey(SequenceAsset)
    # Points to an "Assignment" Project.
    project = models.ForeignKey(Project)

    class Meta:
        unique_together = ('sequence_asset', 'project')
