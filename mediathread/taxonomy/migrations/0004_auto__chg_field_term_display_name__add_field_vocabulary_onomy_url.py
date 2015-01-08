# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Term.display_name'
        db.alter_column(u'taxonomy_term', 'display_name', self.gf('django.db.models.fields.CharField')(max_length=50))
        # Adding field 'Vocabulary.onomy_url'
        db.add_column(u'taxonomy_vocabulary', 'onomy_url',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'Term.display_name'
        db.alter_column(u'taxonomy_term', 'display_name', self.gf('django.db.models.fields.CharField')(max_length=50))
        # Deleting field 'Vocabulary.onomy_url'
        db.delete_column(u'taxonomy_vocabulary', 'onomy_url')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'taxonomy.term': {
            'Meta': {'ordering': "['display_name', 'id']", 'unique_together': "(('name', 'vocabulary'),)", 'object_name': 'Term'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'ordinality': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'vocabulary': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['taxonomy.Vocabulary']"})
        },
        u'taxonomy.termrelationship': {
            'Meta': {'ordering': "['term__display_name', 'id']", 'unique_together': "(('term', 'content_type', 'object_id'),)", 'object_name': 'TermRelationship'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['taxonomy.Term']"})
        },
        u'taxonomy.vocabulary': {
            'Meta': {'ordering': "['display_name', 'id']", 'object_name': 'Vocabulary'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'onomy_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'single_select': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['taxonomy']
