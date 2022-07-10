from rest_framework import status, views, generics
from rest_framework.response import Response

from .permissions import (
    IsAuthenticatedAndVerified,
)
from .serializers import (
    CategorySerializer,
    PostSerializer
)
from .models import (
    Category,
    Comment,
    Post,
)
from accounts.models import (
    User,
    OTPRequest,
)


class PostListView(views.APIView):
    def get(self, request):
        posts = Post.objects.published()
        serializer = PostSerializer(posts, many=True)
        
        return Response(serializer.data)

class PostDetailView(views.APIView):
    def get(self, request, slug):
        try:
            post = Post.objects.get(slug=slug, status='p')
        except Post.DoesNotExist:
            return Response({"error": "post does not exists"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)
        return Response(serializer.data)

class PostCategoryListView(views.APIView):
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug, active=True)
        except Category.DoesNotExist:
            return Response({"error": "category does not exists"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(category.articles.published(), many=True)
        return Response(serializer.data)

class CategoryListView(views.APIView):
    def get(self, request):
        categories = Category.objects.active()
        serializer = CategorySerializer(categories, many=True)
        
        return Response(serializer.data)

class LikeView(views.APIView):
    permission_classes = [IsAuthenticatedAndVerified]
    def post(self, request):
        pass

class CommentView(views.APIView):
    permission_classes = [IsAuthenticatedAndVerified]
