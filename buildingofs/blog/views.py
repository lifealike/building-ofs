from django.template.response import TemplateResponse
from django.views.generic import View

from buildingofs.utils.views import PermissionsMixin

from .models import Post

class PostView(PermissionsMixin, View):
    permissions = {
        "any": ['view_locations'],
    }

    def get(self, request, slug):
        context = {}

        return TemplateResponse(request, 'blog/post.html', context)
