from django.db import models


class Post(models.Model):

    TYPE_BLOG = 'blog'
    TYPE_LINK = 'link'
    TYPE_AD = 'ad'

    POST_TYPES = (
        (TYPE_BLOG, 'Blog'),
        (TYPE_LINK, 'Link'),
        (TYPE_AD, 'Ad'),
    )

    slug = models.SlugField(max_length=255, unique=True)
    title = models.TextField()
    types = models.CharField(max_length=15, choices=POST_TYPES, default=TYPE_BLOG)
    summary = models.TextField()
    live = models.BooleanField(default=False)

    author_id = models.IntegerField(blank=True, null=True)
    body_markdown = models.TextField(blank=True)
    body_html = models.TextField(blank=True)
    link = models.URLField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    @property
    def author(self):
        if not hasattr(self, '_author'):
            try:
                self._author = Staff.objects.get(pk=self.author_id)
            except Staff.DoesNotExist:
                self._author = None
        return self._author

    @author.setter
    def author(self, value):
        self._author = value
        self.authod_id = value.id

