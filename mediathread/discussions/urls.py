from django.urls import path
from mediathread.discussions.views import (
    DiscussionView, DiscussionDeleteView, DiscussionCreateView,
    comment_save
)


urlpatterns = [
    path('create/', DiscussionCreateView.as_view(), name='discussion-create'),

    path('delete/<int:discussion_id>/',
         DiscussionDeleteView.as_view(), {},
         name='discussion-delete'),

    path('comment/<int:comment_id>/',
         comment_save,
         name='comment-save'),

    #  path('comment/<int:comment_id>/',
    #       DiscussionSaveCommentView.as_view(),
    #       name='comment-save'),

    path('<int:discussion_id>/',
         DiscussionView.as_view(), {}, 'discussion-view'),

]
