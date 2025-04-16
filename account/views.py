from rest_framework import generics

from billing.utils import get_active_subscription
from diagram.models import DiagramInvitation
from .serializers import NotificationIdSerializer, NotificationSerializer, RegistrationSerializer, EmailSerializer, EmailOtpSerializer, UserFieldsSerializer, LoginSerializer, UserSerializer, LogoutSerializer
from common.responses import SuccessResponse, ErrorResponse
from common.utils import format_first_error
from .models import Notification, UserAccount
from .services import send_verification_email, confirm_verification_email, get_user_by_email
from common.mixins import ValidatingGenericApiView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


class ReadAllNotificationsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        unread_notifications.update(is_read=True)
        
        return SuccessResponse(message="All notifications read successfully")

class ReadNotification(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationIdSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(message=format_first_error(serializer.errors))
        
        notification_id = serializer.validated_data.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read= True
            notification.save()
        except Notification.DoesNotExist:
            return ErrorResponse(message="Notification not found")
        
        return SuccessResponse(message="Notification read successfully", data=NotificationSerializer(notification).data)

class NotificationsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class LogoutApi(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return ErrorResponse(message=format_first_error(serializer.errors))
        
        validated_data = serializer.validated_data
        refresh_token = validated_data.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, InvalidToken):
            return ErrorResponse(message="Invalid or expired token")
        except Exception as e:
            
            return ErrorResponse(message=f"An error occurred while logging out {e}")
        
        return SuccessResponse(message="User logged out successfully")


class GetUserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    def retrieve(self, request, *args, **kwargs):
        return SuccessResponse(message="User details", data=self.get_serializer(request.user).data)

class UserLoginView(ValidatingGenericApiView):
    """
    Log a user in 
    
    ---
    """
    
    serializer_class = LoginSerializer

    def on_validated(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        user= authenticate(email=email, password=password)
        if not user:
            return ErrorResponse(message="Invalid login details")
        
        if not user.is_active:
            return ErrorResponse(message="This account has been deactivated, please contact support")
        
        if not user.email_verified:
            return ErrorResponse(message="Email is not verified, please complete email verification before login attempt")
        
        refresh = RefreshToken.for_user(user)
        
        return SuccessResponse(message="Login successful", data={
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
            'user': UserFieldsSerializer(user).data
    })


class VerifyAccountView(ValidatingGenericApiView):
    """
    Verify a user account
    
    ---
    """
    serializer_class = EmailOtpSerializer
    def on_validated(self, validated_data):
        email = validated_data.get('email')
        otp = validated_data.get('otp')
        user = get_user_by_email(email)
    
        if user == None:
            return ErrorResponse(message="No account found for the provided email")
        
        if user.email_verified:
            return ErrorResponse(message="Account is already verified, please login")
        
        is_valid = confirm_verification_email(email, otp)
        if is_valid:
            user.email_verified = True
            user.save()
            return SuccessResponse(message="Account verified successfully")
        return ErrorResponse(message="Invalid OTP, please try again")

class ResendVerificationMail(ValidatingGenericApiView):
    """
    Resend user account verification email
    
    ---
    """
    serializer_class = EmailSerializer
    def on_validated(self, validated_data):
        email = validated_data.get('email')
        user = get_user_by_email(email)
        
        if user.email_verified:
            return ErrorResponse(message="Account is already verified, please login")
        
        send_verification_email(email)
        return SuccessResponse(message="Verification email sent successfully")

class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user_password = validated_data.pop('password')
            invitation_id = validated_data.pop('invitation', None)
            
            user = UserAccount.objects.create(**validated_data)
            user.set_password(user_password)
            user.save()
            
            #send verification email
            send_verification_email(user.email)
            return SuccessResponse(message="Account created successfully", data=UserFieldsSerializer(user).data)
            
        else:
            return ErrorResponse(message=format_first_error(serializer.errors)) 