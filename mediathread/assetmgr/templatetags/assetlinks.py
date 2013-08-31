from mediathread.assetmgr.models import Asset
from django import template


def source_url(source, request):
    return source.url_processed(request)

register = template.Library()
register.filter(source_url)


class InCourseNode(template.Node):
    def __init__(self, archive_key, course_key,
                 nodelist_true, nodelist_false=None):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.archive_key = archive_key
        self.course_key = course_key

    def render(self, context):
        archive_key = context[self.archive_key]
        course_key = context[self.course_key]

        lst = Asset.objects.filter(title=archive_key.title, course=course_key)
        for asset in lst:
            if asset.primary and asset.primary.is_archive():
                return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)


@register.tag('ifincourse')
def ifincourse(parser, token):
    try:
        tagname, archive_key, course_key = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires two argument" %
                                           token.contents.split()[0])

    nodelist_true = parser.parse(('else', 'endifincourse'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifincourse',))
        parser.delete_first_token()
    else:
        nodelist_false = None
    return InCourseNode(archive_key, course_key, nodelist_true, nodelist_false)
