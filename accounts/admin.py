from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTPRequest
# Register your models here.

class UserS(admin.ModelAdmin):
    list_display=[
        'avatar'
    ]
admin.site.register(User)

class OTPRequestAdmin(admin.ModelAdmin):
    list_display = [
        'register_id',
        'user',
        'otp', 
        'is_expired',
        'verified',
    ]
    
admin.site.register(OTPRequest, OTPRequestAdmin)