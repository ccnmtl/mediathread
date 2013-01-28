from django import template
from djangohelpers.templatetags import TemplateTagNode

register = template.Library()


class WithPermission(TemplateTagNode):

    noun_for = {"with": "query", "for": "request"}

    def __init__(self, varname, query, request):
        TemplateTagNode.__init__(self, varname, query=query, request=request)

    def execute_query(self, query, request):
        return [c for c in query if c.permission_to('read', request)]


register.tag('with_permission', WithPermission.process_tag)


class IfPermission(TemplateTagNode):

    noun_for = {"with": "collab", "to": "perm", "for": "request"}

    def __init__(self, varname, collab, perm, request):
        TemplateTagNode.__init__(self, varname, collab=collab,
                                 perm=perm, request=request)

    def execute_query(self, collab, perm, request):
        if collab and collab.permission_to(perm, request):
            return collab
        return None


register.tag('if_permission', IfPermission.process_tag)
