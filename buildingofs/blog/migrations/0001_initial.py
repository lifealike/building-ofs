# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Post'
        db.create_table(u'blog_post', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('types', self.gf('django.db.models.fields.CharField')(default='blog', max_length=15)),
            ('summary', self.gf('django.db.models.fields.TextField')()),
            ('live', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('body_markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('body_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('published_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'blog', ['Post'])


    def backwards(self, orm):
        # Deleting model 'Post'
        db.delete_table(u'blog_post')


    models = {
        u'blog.post': {
            'Meta': {'object_name': 'Post'},
            'body_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'body_markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'live': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'types': ('django.db.models.fields.CharField', [], {'default': "'blog'", 'max_length': '15'})
        }
    }

    complete_apps = ['blog']