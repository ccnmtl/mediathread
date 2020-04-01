from django.urls import path

from mediathread.discussions.views import (
    DiscussionView, DiscussionDeleteView, discussion_create,
    comment_save
)


urlpatterns = [
    path('create/', discussion_create, name='discussion-create'),

    path('delete/<int:discussion_id>/',
         DiscussionDeleteView.as_view(), {},
         name='discussion-delete'),

    path('comment/<int:comment_id>/',
         comment_save,
         name='comment-save'),

    path('<int:discussion_id>/',
         DiscussionView.as_view(), {}, 'discussion-view'),

]
