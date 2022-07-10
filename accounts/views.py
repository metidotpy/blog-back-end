from rest_framework import views, status, serializers, generics
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    PasswordResetSerializer,
    RegisterSerializer,
    ProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    EditEmailSerializer,
    EditPhoneSerializer,
    OTPCreatorSerializer,
)

from .senders import (
    send_otp
)

from .models import (
    User,
    OTPRequest,
)

class TokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

class RegisterView(views.APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': 'request'})
        if serializer.is_valid():
            user = serializer.save()
            data = {}
            user.is_active = False
            user.is_activity = False
            user.is_phone_verified = False
            user.is_email_verified = False
            user.save()
            otp = OTPRequest.objects.create(user=user, provider=user.register_provider)
            if user.register_provider == 'p':
                otp.phone = user.phone
                otp.email=None
                otp.save()
                send_otp.send_sms(user.phone, otp.otp)
            elif user.register_provider == 'e':
                otp.email = user.email
                otp.phone=None
                otp.save()
                send_otp.send_email(user.email, otp.otp)
            token = RefreshToken.for_user(user)
            data['register_provider'] = user.register_provider
            data['username'] = user.username
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            data['email'] = user.email
            data['phone'] = user.phone
            data['avatar'] = user.avatar.url
            data['otp_id'] = otp.register_id
            data['otp_phone'] = otp.phone
            data['otp_email'] = otp.email
            data['otp_created'] = otp.created
            data['otp_expired'] = otp.expired
            data['otp'] = otp.otp
            
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(views.APIView):
    def post(self, request):
        data = {}
        try:
            otp = OTPRequest.objects.get(register_id=request.data['register_id'], otp=request.data['otp'])
        except OTPRequest.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        user = otp.user
        if not otp.is_expired():
            user.is_active = True
            user.is_activity = True
            if otp.provider == 'p':
                user.is_phone_verified = True
            elif otp.provider == 'e':
                user.is_email_verified = True
            user.save()
            otp.verified=True
            otp.save()
            token = RefreshToken.for_user(user)
            data['token'] = {
                'refresh': str(token),
                'access': str(token.access_token),
            }
            
            data['verified'] = otp.verified
        else:
            return Response({'error': "time for verification is expired."})

        return Response(data, status=status.HTTP_200_OK)
        

class PasswordChangeView(views.APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        self.user = User.objects.get(pk=request.user.pk)
        serializer = PasswordChangeSerializer(self.user, data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data.get("old_password")
            password = serializer.validated_data.get("password")
            password2 = serializer.validated_data.get("password2")
            if not self.user.check_password(old_password):
                raise serializers.ValidationError({'old_password': "wrong password."})
            
            if password != password2:
                raise serializers.ValidationError({"error": "password does not match."})
            
            self.user.set_password(password)
            self.user.save()
            
            return Response({"success": "password is changed."})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get(self, request):
        try:
            self.user = request.user
            user = User.objects.get(pk = self.user.pk)
        except User.DoesNotExist:
            return Response({'error': "user not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user)
        return Response(serializer.data)
    
    def put(self, request):
        try:
            self.user = request.user
            self.email = self.user.email
            self.phone = self.user.phone
            self.avatar = self.user.avatar.url
            user = User.objects.get(pk = self.user.pk)
        except User.DoesNotExist:
            return Response({'error': "user not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            
            if 'avatar' in serializer.validated_data and serializer.validated_data['avatar'] == None:
                serializer.validated_data['avatar'] = self.avatar

            if 'phone' in serializer.validated_data and self.phone != serializer.validated_data.get("phone"):
                user.email = serializer.validated_data.get('phone')
                user.is_activity = False
                user.is_phone_verified = False
                user.save()
                otp = OTPRequest.objects.create(user=user, provider="p")
                otp.save()
                send_otp.send_sms(serializer.validated_data.get("phone"), otp.otp)
                data['phone_otp'] = "sended."
                data['otp_id'] = otp.register_id
                data['otp_created'] = otp.created
                data['otp_expired'] = otp.expired
                data['otp'] = otp.otp
                
            if 'email' in serializer.validated_data and self.email != serializer.validated_data.get("email"):
                user.email = serializer.validated_data.get('email')
                user.is_activity = False
                user.is_email_verified = False
                user.save()
                otp = OTPRequest.objects.create(user=user, provider="p")
                otp.save()
                send_otp.send_email(serializer.validated_data.get("email"), otp.otp)
                data['email_otp'] = "sended."
                data['otp_id'] = otp.register_id
                data['otp_created'] = otp.created
                data['otp_expired'] = otp.expired
                data['otp'] = otp.otp
            
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(views.APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = {}
            otp, user_selection = serializer.save()
            if user_selection == 'e':
                data['email_otp'] = "sended."
                
            elif user_selection == 'p':
                data['phone_otp'] = "sended."
            
            data['otp_id'] = otp.register_id
            data['otp_created'] = otp.created
            data['otp_expired'] = otp.expired
            data['otp'] = otp.otp
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetVerifyOTP(views.APIView):
    def post(self, request):
        data = {}
        try:
            if 'phone' in request.data:
                user = User.objects.get(phone = request.data.get('phone'))
            elif 'email' in request.data:
                user = User.objects.get(email=request.data.get('email'))
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            otp = OTPRequest.objects.get(user=user, register_id=request.data['register_id'], otp=request.data['otp'])
        except OTPRequest.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not otp.is_expired():
            otp.verified=True
            otp.save()
            data['otp_id'] = otp.register_id
            data['verified'] = otp.verified
        else:
            return Response({'error': "time for verification is expired."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)

class PasswordResetView(views.APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            otp_id = request.data.get('register_id')
            try:
                otp = OTPRequest.objects.get(register_id=otp_id)
            except OTPRequest.DoesNotExist:
                return Response({"error": "INVALID OTP"}, status=status.HTTP_404_NOT_FOUND)
            if not otp.is_expired() and otp.verified:
                user = otp.user
                user.set_password(request.data.get("password"))
                user.save()
                otp.verified=False
                otp.save()
                return Response({"success": "password is changed"})
            else:
                return Response({"error": "otp is not verified or expired"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditEmailView(views.APIView):
    def post(self, request):
        serializer = EditEmailSerializer(data=request.data)
        if serializer.is_valid():
            otp, user = serializer.save()
            otp.delete()
            new_otp = OTPRequest.objects.create(provider='e', user=user, email=user.email, phone=user.phone)
            user.is_email_verified = False
            user.is_activity = False
            user.save()
            send_otp.send_email(email=new_otp.email, otp=new_otp.otp)
            data = {}
            data['otp_id'] = new_otp.register_id
            data['otp_email'] = new_otp.email
            data['otp_phone'] = new_otp.phone
            data['otp'] = new_otp.otp
            return Response(data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

class EditPhoneView(views.APIView):
    def post(self, request):
        serializer = EditPhoneSerializer(data=request.data)
        if serializer.is_valid():
            otp, user = serializer.save()
            otp.delete()
            new_otp = OTPRequest.objects.create(provider='p', user=user, email=user.email, phone=user.phone)
            user.is_phone_verified = False
            user.is_activity = False
            user.save()
            send_otp.send_sms(phone=new_otp.phone, otp=new_otp.otp)
            data = {}
            data['otp_id'] = new_otp.register_id
            data['otp_email'] = new_otp.email
            data['otp_phone'] = new_otp.phone
            data['otp'] = new_otp.otp
            return Response(data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPRefreshView(views.APIView):
    def post(self, request):
        serializer = OTPCreatorSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.save()
            user = otp.user
            user.is_phone_verified = False
            user.is_activity = False
            user.save()
            if otp.phone:
                send_otp.send_sms(otp.phone, otp.otp)
            elif otp.email:
                send_otp.send_email(otp.email, otp.otp)
            data = {}
            data['otp_id'] = otp.register_id
            data['otp_email'] = otp.email
            data['otp_phone'] = otp.phone
            data['otp'] = otp.otp
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)