from django.template import Library, loader, Context

register = Library()


@register.simple_tag(takes_context=True)
def render_post(context, post):
    template_name = "blog/snippets/{}.html".format(post.post_type)
    context = {
        "post": post,
    }
    template = loader.get_template(template_name)
    return template.render(Context(context))
