from atexit import register
from django.contrib import admin
from .models import (
    Post,
    Category,
    IPAddress,
    Comment,
)

# Register your models here.

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(IPAddress)
admin.site.register(Comment)