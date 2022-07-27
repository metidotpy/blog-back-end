from requests import post
from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .permissions import (
    IsAuthenticatedAndVerified,
)
from .serializers import (
    CategorySerializer,
    PostSerializer,
    CommentSerializer,
    CommentLikeSerializer,
    CommentShowSerializer,
    CommentUpdateSerializer,
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
        comments = serializer.data.get("comments")
        for comment in comments:
            # print(comment)
            if 'is_replied' in comment and comment.get("is_replied"):
                if "comment_replied" in comment and comment.get("comment_replied"):
                    comment_replied = comment.get("comment_replied")    
                    for _ in comments:
                        if _.get("id") == comment_replied:
                            primary_comment = _
                            primary_comment['replies'] = []
                            break
                    primary_comment['replies'].append(comment)
                    print(primary_comment['replies'])
        ip_address = request.ip_address
        if ip_address not in post.hits.all():
            post.hits.add(ip_address)
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
    def post(self, request, slug):
        try:
            post = Post.objects.get(status='p', slug=slug)
        except Post.DoesNotExist:
            return Response({"error": "post does not exists"}, status=status.HTTP_404_NOT_FOUND)

        if request.user not in post.likes.all():
            post.likes.add(request.user)
            post.save()
            serializer = PostSerializer(post)
            data = serializer.data
            data['liked']='post liked successfully'
        else:
            post.likes.remove(request.user)
            post.save()
            serializer = PostSerializer(post)
            data = serializer.data
            data['unliked']='post unliked successfully'
        
        return Response(data)


class CommentView(views.APIView):
    permission_classes = [IsAuthenticatedAndVerified]
    
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug, status='p')
        except Post.DoesNotExist:
            return Response({"error": "post does not exists"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(user=request.user)
            post.comments.add(comment)
            data = {}
            post_serializer = PostSerializer(post)
            data['post'] = post_serializer.data
            data['comment'] = serializer.data
            data['comment']['id'] = comment.id
            data['comment']['user'] = comment.user.username
            if 'is_replied' in serializer.validated_data and serializer.validated_data.get('is_replied'):
                data['comment']['user_replied'] = comment.user_replied.username
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CommentListView(views.APIView):
    def get(self, request, slug):
        try:
            post = Post.objects.get(slug=slug, status='p')
        except Post.DoesNotExist:
            return Response({"error": "post does not exists"}, status=status.HTTP_404_NOT_FOUND)
        
        comments = post.comments.all()
        serializer = CommentShowSerializer(comments, many=True)
        return Response(serializer.data)
    
class CommentLikeView(views.APIView):
    permission_classes = [IsAuthenticatedAndVerified]
    def post(self, request):
        user = request.user
        serializer = CommentLikeSerializer(data=request.data)
        if serializer.is_valid():
            data = {}
            id = serializer.validated_data.get('id')
            try:
                comment = Comment.objects.get(pk=id)
            except Comment.DoesNotExist:
                return Response({"error": "comment does not exists"}, status=status.HTTP_404_NOT_FOUND)
            data['comment'] = CommentShowSerializer(comment).data
            if user not in comment.likes.all():
                comment.likes.add(user)
                comment.save()
                data['status'] = "liked"
            else:
                comment.likes.remove()
                comment.save()
                data['status'] = "unliked"
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLikeListView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        posts = Post.objects.filter(likes__in=user)
        
        serializer = PostSerializer(posts, many=True)
        
        return Response(serializer.data)

class UserCommentListView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        comments = Post.objects.filter(comments__user = user)
        
        serializer = PostSerializer(comments, many=True)
        
        return Response(serializer.data)

class CommentUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, pk):
        try:
            comment = Comment.objects.get(pk = pk, user = request.user)
        except Comment.DoesNotExist:
            return Response({"error": "comment does not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CommentUpdateSerializer(comment, data=request.data)
        if serializer.is_valid():
            if comment.is_editable():
                comment.is_edited = True
                comment.save()
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"error": "You can't edit this comment, edit time is expired"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk = pk, user = request.user)
        except Comment.DoesNotExist:
            return Response({"error": "comment does not found"}, status=status.HTTP_404_NOT_FOUND)
        
        comment.delete()
        return Response({"message": "deleted"}, status =status.HTTP_204_NO_CONTENT)