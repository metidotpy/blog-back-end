from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone
import random, string, os, uuid
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import ImageField, get_thumbnail

def create_expired_time():
    return timezone.now() + timedelta(minutes=30)

def create_refresh_time():
    return timezone.now() + timedelta(minutes=2)

def otp_generator():
    return ''.join(random.choices(string.digits, k=6))

def random_avatar_image_url():
    return f"avatar/defaults/default-{random.randint(0, 9)}.png"

def split_ext(file):
        base_name = os.path.basename(file)
        name, ext = os.path.splitext(base_name)

        return name, ext

def upload_path(instance,  filepath):
        name, ext = split_ext(filepath)
        new_name = random.randint(0, 9999999999)
        return f"avatar/{instance.username}/{instance.id}/{new_name}{ext}"
        

# Create your models here.

class UnicodeUsernameValidator(RegexValidator):
    regex = r"^[\w.]+\Z"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and ./_ characters."
    )
    flags = 0

class PhoneNumberValidator(RegexValidator):
    regex = r'^(?:98|\+98|0098|0)?9[0-9]{9}$'
    message = "Phone number must be entered in the format: '+989012345678'. Up to 15 digits allowed."
    

class User(AbstractUser, PermissionsMixin):
    REGISTER_PROVIDER = (
        ('p', 'phone'),
        ('e', 'email'),
    )
    register_provider = models.CharField(
        max_length=1,
        choices=REGISTER_PROVIDER,
        default='p',
    )
    username_validator = UnicodeUsernameValidator()
    phone_validator = PhoneNumberValidator()
    
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    
    username = models.CharField(
        unique=True,
        max_length=60,
        validators=[username_validator],
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )
    phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        unique=True,
        validators=[phone_validator],
    )
    avatar = models.ImageField(
        upload_to = upload_path,
        default=random_avatar_image_url, 
        null=True,
        blank=True,
    )
    
    is_author = models.BooleanField(default=False)
    is_activity = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_deactive = models.BooleanField(default=False)
    
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.avatar:
            self.avatar = get_thumbnail(self.avatar, '200x200', quality=99, format="JPEG")
        super(User, self).save(*args, **kwargs)


class OTPRequest(models.Model):
    PROVIDERS = (
        ('p', 'phone'),
        ('e', 'email'),
        ('r', "reset password"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, null=True, blank=True, validators=[PhoneNumberValidator])
    register_id = models.UUIDField(primary_key=True, max_length=40, default=uuid.uuid4, unique=True,)
    provider = models.CharField(max_length=1, choices=PROVIDERS, default='p')
    otp = models.CharField(max_length=6, default=otp_generator)
    verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expired = models.DateTimeField(default=create_expired_time)
    refresh = models.DateTimeField(default=create_refresh_time)
    
    def is_expired(self):
        if self.expired < timezone.now():
            return True
        return False
    
    def is_refreshed(self):
        if self.refresh < timezone.now():
            return True
        return False