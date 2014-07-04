# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Post.types'
        db.delete_column(u'blog_post', 'types')

        # Adding field 'Post.post_type'
        db.add_column(u'blog_post', 'post_type',
                      self.gf('django.db.models.fields.CharField')(default='blog', max_length=15),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Post.types'
        db.add_column(u'blog_post', 'types',
                      self.gf('django.db.models.fields.CharField')(default='blog', max_length=15),
                      keep_default=False)

        # Deleting field 'Post.post_type'
        db.delete_column(u'blog_post', 'post_type')


    models = {
        u'blog.post': {
            'Meta': {'object_name': 'Post'},
            'author_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'body_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'body_markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'live': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'post_type': ('django.db.models.fields.CharField', [], {'default': "'blog'", 'max_length': '15'}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['blog']