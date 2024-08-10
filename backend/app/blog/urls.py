from django.urls import path
from . import views
urlpatterns = [
    path('create-post/',views.CreatePostView.as_view(),name='CreatePost'),
    path('post/',views.ReadAllPostView.as_view(),name='read_all_posts'),
    path('post/<int:post_id>/publish/', views.PublishedPostView.as_view(), name='publish_post_api'),
    path('mypost/',views.ReadUserAllPostView.as_view(),name='read-all-user-posts'),
    path('post/<int:post_id>/delete/',views.DeletePostView.as_view(),name='delete-post'),
    path('post/<int:post_id>/update/',views.UpdatePostView.as_view(),name='update-post'),
    path('post/like/<int:post_id>/',views.LikeCreateView.as_view(),name='create-like'),
    path('post/dis-like/<int:post_id>/',views.LikeDeleteView.as_view(),name='like-delete'),
    path('post/comments/<int:post_id>/',views.CommentCreateView.as_view(),name='create-comment'),
    path('post/<int:post_id>/comments/',views.CommentReadView.as_view(),name='read-comments'),
    path('post/<int:post_id>/comment/<int:comment_id>/delete/',views.CommentDeleteView.as_view(),name='delete-comments'),
    path('post/<int:post_id>/comment/<int:comment_id>/update/',views.CommentUpdateView.as_view(),name='update-comments'),

    path('post/<int:post_id>/share-options/', views.ShareOptionsView.as_view(), name='share-options'),
    path('post/<int:post_id>/share/', views.ShareView.as_view(), name='share'),
]
