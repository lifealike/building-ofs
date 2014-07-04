from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import View

from buildingofs.utils.views import PermissionsMixin

from .models import Post


class PostView(View):

    def get(self, request, slug):

        post = get_object_or_404(Post, slug=slug)

        context = {
            "post": post,
        }

        return TemplateResponse(request, 'blog/post.html', context)
