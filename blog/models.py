from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User
# from .models import Comment

# Create your managers here.

class CategoryManager(models.Manager):
    def active(self):
        return self.filter(active = True)

class PostManager(models.Manager):
    def published(self):
        return self.filter(status='p')
    
    def drafted(self):
        return self.filter(status='d')
    
    def declined(self):
        return self.filter(status='d')
    
    def investigation(self):
        return self.filter(status='i')

# Create your models here.




class IPAddress(models.Model):
    ip_address = models.GenericIPAddressField()

class Category(models.Model):
    title = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CategoryManager()
    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(max_length=200)
    is_replied = models.BooleanField(default=False)
    user_replied = models.ForeignKey(User, related_name='user_replied_comments', on_delete=models.CASCADE)
    
    def clean(self):
        if self.is_replied:
            if not self.user_replied:
                raise ValidationError("user_replied is required.")
        return super().clean()

class Post(models.Model):
    STATUS_CHOICES = (
        ('d', 'declined'),
        ('p', 'published'),
        ('i', 'investigation'),
        ('d', 'draft'),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ManyToManyField(Category, related_name='articles')
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='blog/images/')
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    comments = models.ManyToManyField(Comment, related_name='comments', blank=True)
    hits = models.ManyToManyField(IPAddress, through="PostHit", blank=True, related_name='hits')
    likes = models.ManyToManyField(User, related_name="post_like", blank=True)

    objects = PostManager()

class PostHit(models.Model):
    article = models.ForeignKey(Post, on_delete=models.CASCADE)
    ip_address = models.ForeignKey(IPAddress, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)