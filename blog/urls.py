from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.PostListView.as_view(), name='post-list'),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name='post-detail'),
    path("category/", views.CategoryListView.as_view(), name='categories'),
    path("category/<slug:slug>/post/", views.PostCategoryListView.as_view(), name='posts_category'),
]
