# flake8: noqa
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Vocabulary'
        db.create_table('taxonomy_vocabulary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('single_select', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('taxonomy', ['Vocabulary'])

        # Adding model 'Term'
        db.create_table('taxonomy_term', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('vocabulary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['taxonomy.Vocabulary'])),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ordinality', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('taxonomy', ['Term'])

        # Adding unique constraint on 'Term', fields ['name', 'vocabulary']
        db.create_unique('taxonomy_term', ['name', 'vocabulary_id'])

        # Adding model 'TermRelationship'
        db.create_table('taxonomy_termrelationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['taxonomy.Term'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('taxonomy', ['TermRelationship'])

        # Adding unique constraint on 'TermRelationship', fields ['term', 'content_type', 'object_id']
        db.create_unique('taxonomy_termrelationship', ['term_id', 'content_type_id', 'object_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'TermRelationship', fields ['term', 'content_type', 'object_id']
        db.delete_unique('taxonomy_termrelationship', ['term_id', 'content_type_id', 'object_id'])

        # Removing unique constraint on 'Term', fields ['name', 'vocabulary']
        db.delete_unique('taxonomy_term', ['name', 'vocabulary_id'])

        # Deleting model 'Vocabulary'
        db.delete_table('taxonomy_vocabulary')

        # Deleting model 'Term'
        db.delete_table('taxonomy_term')

        # Deleting model 'TermRelationship'
        db.delete_table('taxonomy_termrelationship')


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
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
