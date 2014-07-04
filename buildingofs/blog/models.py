from django.db import models
import markdown

from buildingofs.staff.models import Staff


class Post(models.Model):

    TYPE_BLOG = 'blog'
    TYPE_LINK = 'link'
    TYPE_AD = 'ad'
    TYPE_YOUTUBE = 'youtube'

    DISCUSSION_TYPE_REDDIT = "reddit"
    DISCUSSION_TYPE_HN = "hackernews"

    POST_TYPES = (
        (TYPE_BLOG, 'Blog'),
        (TYPE_LINK, 'Link'),
        (TYPE_AD, 'Ad'),
        (TYPE_YOUTUBE, 'Youtube')
    )

    slug = models.SlugField(max_length=255, unique=True)
    title = models.TextField()
    post_type = models.CharField(max_length=15, choices=POST_TYPES, default=TYPE_BLOG)
    summary = models.TextField()
    live = models.BooleanField(default=False)

    author_id = models.IntegerField(blank=True, null=True)

    body_markdown = models.TextField(blank=True)
    body_html = models.TextField(blank=True)

    link = models.URLField(max_length=255, blank=True)
    link_text = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    discussion_link = models.URLField(blank=True)

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

    def discussion_forum(self):
        if 'reddit.com' in self.discussion_link:
            return self.DISCUSSION_TYPE_REDDIT

        if 'ycombinator.com' in self.discussion_link:
            return self.DISCUSSION_TYPE_HN

        return None

    def save(self, *args, **kwargs):

        if self.body_markdown:
            self.body_html = markdown.markdown(self.body_markdown)

        return super(Post, self).save(*args, **kwargs)

