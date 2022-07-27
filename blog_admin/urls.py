from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.PostListView.as_view(), name='post_list'),
    path("category/", views.CategoryListView.as_view(), name='category_list'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('comment/<int:pk>/', views.CommentDetailView.as_view(), name="comment_delete"),
]
