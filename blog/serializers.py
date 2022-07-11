from xml.dom import ValidationErr
from rest_framework import serializers
from .models import (
    Category,
    Post,
    Comment,
)
from rest_framework.fields import CurrentUserDefault


class CommentLikeSerializer(serializers.ModelSerializer):
    # likes = serializers.StringRelatedField(many=True, read_only=True, allow_null=True)
    id = serializers.IntegerField()
    class Meta:
        model = Comment
        fields = ['id']

class CommentReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    likes = serializers.StringRelatedField(read_only=True, many=True, allow_null=True)
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'likes', 'likes_count']

class CommentShowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_replied = serializers.StringRelatedField()
    comment_replied = CommentReplySerializer(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    likes = serializers.StringRelatedField(read_only=True, many=True, allow_null=True)
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'is_replied', 'user_replied', 'comment_replied', 'likes', 'likes_count']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_replied = serializers.StringRelatedField()
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'is_replied', 'user_replied', 'comment_replied']
    
    def save(self, user):
        user=user
        text = self.validated_data.get('text')
        is_replied = self.validated_data.get('is_replied')
        if is_replied:
            if 'comment_replied' not in self.validated_data:
                raise serializers.ValidationError({'error': "comment_replied is required"})
            comment_replied = self.validated_data.get('comment_replied')
            comment_replied_id = comment_replied.id
            try:
                old_comment = Comment.objects.get(id=comment_replied_id)
            except Comment.DoesNotExist:
                raise ValidationErr({"error": "comment does not exists"})
            user_replied = old_comment.user
            comment = Comment.objects.create(user=user, text=text, user_replied=user_replied, comment_replied=comment_replied, is_replied=is_replied)
        else:
            comment = Comment.objects.create(user=user, text=text)
        
        comment.save()
        return comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True, many=True)
    comments = CommentSerializer(many=True)
    likes = serializers.StringRelatedField(read_only=True, many=True)
    hits_count = serializers.IntegerField(source = "hits.count", read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    class Meta:
        model = Post
        fields = [
            'pk',
            'author',
            'title',
            'slug',
            'category',
            'thumbnail',
            'publish',
            'created',
            'updated',
            'status',
            'comments',
            'hits',
            'likes',
            'hits_count',
            'likes_count',
            'comments_count',
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title', 'slug',]