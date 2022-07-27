from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.PostListView.as_view(), name='post-list'),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name='post-detail'),
    path("category/", views.CategoryListView.as_view(), name='categories'),
    path("category/<slug:slug>/post/", views.PostCategoryListView.as_view(), name='posts_category'),
    path("like/post/<slug:slug>/", views.LikeView.as_view(), name='like'),
    path("comment/post/<slug:slug>/", views.CommentListView.as_view(), name='comments_list'),
    path('comment/post/<slug:slug>/create/', views.CommentView.as_view(), name='comment_create'),
    path("comment/like/", views.CommentLikeView.as_view(), name='comment_like'),
    path("like/user/", views.UserLikeListView.as_view(), name='like_list'),
    path("comment/user/", views.UserCommentListView.as_view(), name='comment_list'),
    path("comment/update/<int:pk>/", views.CommentUpdateView.as_view(), name="comment_update")
]
