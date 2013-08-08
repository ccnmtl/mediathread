# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CourseInformation.sample_course'
        db.add_column('course_courseinformation', 'sample_course', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'CourseInformation.course_uuid'
        db.add_column('course_courseinformation', 'course_uuid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True), keep_default=False)

        # Changing field 'CourseInformation.course'
        db.alter_column('course_courseinformation', 'course_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courseaffils.Course'], null=True))

        # Changing field 'CourseInformation.organization'
        db.alter_column('course_courseinformation', 'organization_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_accounts.OrganizationModel'], null=True))


    def backwards(self, orm):
        
        # Deleting field 'CourseInformation.sample_course'
        db.delete_column('course_courseinformation', 'sample_course')

        # Deleting field 'CourseInformation.course_uuid'
        db.delete_column('course_courseinformation', 'course_uuid')

        # User chose to not deal with backwards NULL issues for 'CourseInformation.course'
        raise RuntimeError("Cannot reverse this migration. 'CourseInformation.course' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'CourseInformation.organization'
        raise RuntimeError("Cannot reverse this migration. 'CourseInformation.organization' and its values cannot be restored.")


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'course.courseinformation': {
            'Meta': {'object_name': 'CourseInformation'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courseaffils.Course']", 'null': 'True'}),
            'course_uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_accounts.OrganizationModel']", 'null': 'True'}),
            'sample_course': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_amount': ('django.db.models.fields.IntegerField', [], {})
        },
        'courseaffils.course': {
            'Meta': {'object_name': 'Course'},
            'faculty_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'faculty_of'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'user_accounts.organizationmodel': {
            'Meta': {'object_name': 'OrganizationModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['course']
