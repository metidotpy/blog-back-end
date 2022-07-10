from rest_framework import serializers
from .models import (
    Category,
    Post,
)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True, many=True)
    comments = serializers.StringRelatedField(read_only=True, many=True)
    hits_count = serializers.IntegerField(source = "hits.count", read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    class Meta:
        model = Post
        fields = [
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
        