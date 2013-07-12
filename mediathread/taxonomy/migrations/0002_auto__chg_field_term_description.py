# flake8: noqa
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Term.description'
        db.alter_column('taxonomy_term', 'description', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))


    def backwards(self, orm):
        
        # Changing field 'Term.description'
        db.alter_column('taxonomy_term', 'description', self.gf('django.db.models.fields.TextField')(null=True))


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taxonomy.term': {
            'Meta': {'unique_together': "(('name', 'vocabulary'),)", 'object_name': 'Term'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'ordinality': ('django.db.models.fields.IntegerField', [], {}),
            'vocabulary': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['taxonomy.Vocabulary']"})
        },
        'taxonomy.termrelationship': {
            'Meta': {'unique_together': "(('term', 'content_type', 'object_id'),)", 'object_name': 'TermRelationship'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['taxonomy.Term']"})
        },
        'taxonomy.vocabulary': {
            'Meta': {'object_name': 'Vocabulary'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'single_select': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['taxonomy']
