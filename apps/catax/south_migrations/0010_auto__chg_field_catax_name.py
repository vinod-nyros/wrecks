# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Catax.name'
        db.alter_column(u'catax', 'name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150))


    def backwards(self, orm):
        
        # Changing field 'Catax.name'
        db.alter_column(u'catax', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True))


    models = {
        'catax.catax': {
            'Meta': {'unique_together': "(('county', 'tax'),)", 'object_name': 'Catax', 'db_table': "u'catax'"},
            'cities': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '3000', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['catax']
