from mediathread.djangosherd.models import DiscussionIndex


class DiscussionIndexResource(object):

    def render_list(self, request, indicies):
        collaborations = DiscussionIndex.with_permission(request, indicies)

        ctx = {
            'references': [{
                'id': obj.collaboration.object_pk,
                'title': obj.collaboration.title,
                'type': obj.get_type_label(),
                'url': obj.get_absolute_url(),
                'modified': obj.modified.strftime("%m/%d/%y %I:%M %p")}
                for obj in collaborations]}

        return ctx
