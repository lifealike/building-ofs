from django.template.response import TemplateResponse
from django.views.generic import View

from buildingofs.blog.models import Post


class HomepageView(View):

    def get(self, request):

        posts = Post.objects.filter(live=True)
        context = {
            "posts": posts
        }

        return TemplateResponse(request, 'homepage.html', context)
