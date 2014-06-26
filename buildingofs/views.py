from django.template.response import TemplateResponse
from django.views.generic import View


class HomepageView(View):

    def get(self, request):
        context = {}

        return TemplateResponse(request, 'homepage.html', context)
