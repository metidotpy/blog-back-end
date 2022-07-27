from rest_framework import generics, views, status, serializers
from rest_framework.response import Response

from blog.models import Category, Post, Comment

from .permissions import(
    IsSuperuserOrIsAdmin,
    IsSuperuserOrIsAdminOrIsAuthor,
    IsSuperuserOrIsAdminOrIsAuthorOfPost,
)
from .serializers import (
    PostSerializer,
    PostUpdateSerializer,
    CategorySerializer,
    CategoryUpdateSerializer,
)

class PostListView(views.APIView):
    permission_classes = [IsSuperuserOrIsAdminOrIsAuthor]
    
    def get(self, request):
        if request.user.is_superuser or request.user.is_staff:
            posts = Post.objects.all()
        else:
            posts = Post.objects.filter(author=request.user)
        serializer = PostSerializer(posts, many=True)
        
        return Response(serializer.data)
    
    def post(self, request):
        request.data['author'] = request.user.pk
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.is_superuser or not request.user.is_staff:
                if status not in ['i', 'd']:
                    serializer.validated_data['status'] = 'd'
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryListView(views.APIView):
    permission_classes = [IsSuperuserOrIsAdmin]
    
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetailView(views.APIView):
    permission_classes = [IsSuperuserOrIsAdminOrIsAuthor]
    def get(self, request, slug):
        try:
            if request.user.is_superuser or request.user.is_staff:
                post = Post.objects.get(slug=slug)
            else:
                post = Post.objects.get(slug=slug, author=request.user)
        except Post.DoesNotExist:
            return Response({"error": "post does not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, slug):
        request.data['author'] = request.user.pk
        try:
            if request.user.is_superuser or request.user.is_staff:
                post = Post.objects.get(slug=slug)
            else:
                post = Post.objects.get(slug=slug, author=request.user)
        except Post.DoesNotExist:
            return Response({"error": "post does not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PostUpdateSerializer(post, data=request.data)
        if serializer.is_valid():
            if not request.user.is_superuser or not request.user.is_staff:
                if serializer.validated_data.get('status') not in ['d', 'i']:
                    serializer.validated_data['status'] = 'd'
                
                if "category" in serializer.validated_data:
                    for category in serializer.validated_data.get("category"):
                        if not category.active:
                            raise serializers.ValidationError({"category": [f"Invalid pk \"{category.id}\" - object does not exist."]})
            serializer.save()
            
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, slug):
        try:
            if request.user.is_superuser or request.user.is_staff:
                post = Post.objects.get(slug=slug)
            else:
                post = Post.objects.get(slug=slug, author=request.user)
        except Post.DoesNotExist:
            return Response({"error": "post does not found"}, status=status.HTTP_404_NOT_FOUND)
        
        post.delete()
        return Response({"message": "deleted"}, status =status.HTTP_204_NO_CONTENT)
class CategoryDetailView(views.APIView):
    permission_classes = [IsSuperuserOrIsAdmin]
    
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response({"error": "category does not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    def put(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response({"error": "category does not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategoryUpdateSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response({"error": "category does not found"}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()

        return Response({"message": "deleted"}, status =status.HTTP_204_NO_CONTENT)
    
class CommentDetailView(views.APIView):
    permission_classes = [IsSuperuserOrIsAdmin]
    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"error": "comment does not found"}, status=status.HTTP_404_NOT_FOUND)
        
        comment.delete()
        return Response({"message": "deleted"}, status =status.HTTP_204_NO_CONTENT)