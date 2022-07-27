from rest_framework import serializers
from blog.models import Comment, IPAddress, Category, Post
from accounts.models import User, OTPRequest


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        extra_kwargs = {
            'author': {'allow_null': True, 'required': False},
            'title': {'allow_null': True, 'required': False},
            'slug': {'allow_null': True, 'required': False},
            'category': {'allow_null': True, 'required': False, "many": True},
            'thumbnail': {'allow_null': True, 'required': False},
            'status': {'allow_null': True, 'required': False},
            'description': {'allow_null': True, 'required': False},
        }

class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        extra_kwargs = {
            "title": {"allow_null": True, "required": False},
            "slug": {"allow_null":True, "required": False},
            "active": {"allow_null": True, "required": False},
        }