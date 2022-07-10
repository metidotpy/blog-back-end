from rest_framework.serializers import ValidationError
from rest_framework import serializers
from .models import User, OTPRequest
import re
from .senders import send_otp
from drf_recaptcha.fields import ReCaptchaV2Field


def phone_number(phone):
    if phone.startswith("09"):
        phone = "".join("+98" + phone[1::])
    elif phone.startswith("9"):
        phone = "+98"+phone
    elif phone.startswith("0098"):
        phone = "".join("+" + phone[2::])
    
    return phone

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    avatar = serializers.ImageField(required=False)
    class Meta:
        model = User
        fields = ['register_provider', 'username', 'first_name', 'last_name', 'email', 'phone', 'avatar', 'password', 'password2']
    
    
    def save(self):
        register_provider = self.validated_data.get('register_provider')
        username = self.validated_data.get('username')
        first_name = self.validated_data.get('first_name')
        last_name = self.validated_data.get('last_name')
        avatar = self.validated_data.get("avatar")
        password = self.validated_data.get('password')
        password2 = self.validated_data.get('password2')
        recaptcha = self.validated_data.get("recaptcha")
        print(recaptcha)

        if register_provider == 'p':
            if 'phone' in self.validated_data:
                phone = self.validated_data.get('phone')
                phone = phone_number(phone)
                email = None
            else:
                raise serializers.ValidationError({'error': "Phone is required"})
        elif register_provider == 'e':
            if 'email' in self.validated_data:
                email = self.validated_data.get('email')
                phone = None
            else:
                raise serializers.ValidationError({'error': '"Email is required"'})
        
        if password != password2:
            raise serializers.ValidationError({'error': "Passwords must be same"})
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationErr({'error': "User with this username already exists"})
        
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationErr({'error': "User with this email already exists"})
        
        if phone:
            if User.objects.filter(phone=phone).exists():
                raise serializers.ValidationErr({'error': "User with this phone already exists"})
        
        if avatar:
            user = User.objects.create(register_provider = register_provider, username=username, first_name=first_name, last_name=last_name, email=email, phone=phone, avatar=avatar, is_activity=False, is_phone_verified=False, is_email_verified=False)
        else:
            user = User.objects.create(register_provider = register_provider, username=username, first_name=first_name, last_name=last_name, email=email, phone=phone, is_activity=False, is_phone_verified=False, is_email_verified=False)
        user.set_password(password)
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'avatar',
        ]

class PasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['old_password', 'password', 'password2']


class PasswordResetRequestSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    def validate_email_or_phone(self, value):
        phone_regex = r"^(?:98|\+98|0098|0)?9[0-9]{9}$"
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if re.match(email_regex, value) or re.match(phone_regex, value):
            if re.match(email_regex, value):
                return value
            elif re.match(phone_regex, value):
                value = phone_number(value)
                return value
            else:
                raise serializers.ValidationError({'error': "enter email or phone correctly"})
        else:
            raise serializers.ValidationError({'error': "enter email or phone correctly"})
    
    def save(self):
        phone_regex = r"^(?:98|\+98|0098|0)?9[0-9]{9}$"
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        email_or_phone = self.validated_data.get("email_or_phone")
        if re.match(phone_regex, email_or_phone):
            user_selection = "p"
            try:
                user = User.objects.get(phone=email_or_phone)
            except User.DoesNotExist:
                raise ValidationError({'error': "User does not exists."})
        
        elif re.match(email_regex, email_or_phone):
            user_selection = 'e'
            try:
                user = User.objects.get(email=email_or_phone)
            except User.DoesNotExist:
                raise ValidationError({'error': "User does not exists."})
        else:
            raise ValidationError({'error': "Enter email of phone number correctly"})
        
        otp = OTPRequest.objects.create(user=user, provider='r')
        otp.save()
        if user_selection == 'p':
            send_otp.send_sms(user.phone, otp.otp)
        elif user_selection == 'e':
            send_otp.send_email(user.email, otp.otp)
        
        return otp, user_selection

class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    def save(self):
        password = self.validated_data.get('password')
        password2 = self.validated_data.get('password2')
        
        if password != password2:
            raise ValidationError({"error": "Password does not the same."})

class EditEmailSerializer(serializers.ModelSerializer):
    register_id = serializers.CharField(allow_null = False)
    class Meta:
        model = User
        fields = ['email', 'register_id']
        extra_kwargs = {
            'email': {
                'allow_null': False
            }
        }
    
    def save(self):
        register_id = self.validated_data.get("register_id")
        email = self.validated_data.get("email")
        
        try:
            otp = OTPRequest.objects.get(register_id = register_id)
        except OTPRequest.DoesNotExist:
            raise serializers.ValidationError({'error': "user does not exists."})
        user = otp.user
        user.email = email
        user.save()
        return otp, user

class EditPhoneSerializer(serializers.ModelSerializer):
    register_id = serializers.CharField(allow_null = False)
    class Meta:
        model = User
        fields = ['phone', 'register_id']
        extra_kwargs = {
            'phone': {
                'allow_null': False
            }
        }
    
    def save(self):
        register_id = self.validated_data.get("register_id")
        phone = self.validated_data.get("phone")
        
        try:
            otp = OTPRequest.objects.get(register_id = register_id)
        except OTPRequest.DoesNotExist:
            raise serializers.ValidationError({'error': "user does not exists."})
        user = otp.user
        user.phone = phone
        user.save()
        return otp, user

class OTPCreatorSerializer(serializers.ModelSerializer):
    old_register_id = serializers.CharField(max_length=40, allow_null=False)
    class Meta:
        model = OTPRequest
        fields = ['old_register_id']
    
    def save(self):
        old_register_id = self.validated_data.get("old_register_id")
        
        try:
            old_otp = OTPRequest.objects.get(register_id=old_register_id)
        except OTPRequest.DoesNotExist:
            raise ValidationError({"error": "otp does not exists"})
        
        if old_otp.is_refreshed():
            if old_otp.provider == 'p':
                if old_otp.phone:
                    phone = old_otp.phone
                    email = None
                else:
                    raise ValidationError({"error": "you don't have phone number"})
            elif old_otp.provider == 'e':
                if old_otp.email:
                    email = old_otp.email
                    phone = None
                else:
                    raise ValidationError({"error": "you don't have phone number"})
            
            otp = OTPRequest.objects.create(user=old_otp.user, email=email, phone=phone, provider=old_otp.provider)
            otp.save()
            old_otp.delete()
            return otp
        else:
            raise ValidationError({"error": "you must wait 2 minutes"})