

#! Django utilities and views
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

#! DRF components for API handling
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
#! JWT for token generation and handling
import jwt
#! Application-specific modules
from .models import CustomUser,Profile
from .serializers import CustomUserSerializers, LoginSerializers,ProfileSerializers
from app.accounts.utils.generate_Token import generate_verification_token
from app.accounts.utils.form_validation import validation_email, validation_password

#! Standard library imports
import datetime



#! View here

#! SignupViews is a class-based view that handles user registration.
class SignupViews(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializers = CustomUserSerializers(data=request.data)
            if serializers.is_valid():
                serializers.save()
                return Response({'Response': 'user created successfully'}, status=status.HTTP_201_CREATED)
            return Response({'ResponseError': serializers.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


#! LoginViews is a class-based view that handles user login.
class LoginViews(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializers = LoginSerializers(data=request.data)
            if serializers.is_valid():
                user = serializers.validated_data['user']
                login(request, user)
                refresh = RefreshToken.for_user(user)
                print('refreshToken', str(refresh))
                response = Response({
                    'access': str(refresh.access_token),
                    'loginuser': user.username,
                    'response': 'Login successful',
                }, status=status.HTTP_200_OK)
                response.set_cookie('refresh_token', str(refresh), httponly=True, samesite='None')
                return response
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


#! LogoutViews is a class-based view that handles user logout.
class LogoutViews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logout(request)

            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response({'Response': 'Logout successful'}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            return response
        except Exception as e:
            return Response({'ResponseError': str(e)}, status=status.HTTP_400_BAD_REQUEST)



#! Define a view to handle sending email verification link
class SendEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.email_verified:
            try:
                token = generate_verification_token(user.pk)

                user.token_created_at = timezone.now()
                user.token_expiry_time = timezone.now() + datetime.timedelta(minutes=30)
                user.save()

                verification_link = f"{settings.FRONTEND_URL}/verify_email/?token={token}"
                send_mail(
                    'Email Verification Request',
                    f"Here is your email verification link: {verification_link}",
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                return Response({'message': 'Verification email sent successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'message': 'Email is already verified'}, status=status.HTTP_400_BAD_REQUEST)


#! Define a view to handle the email verification
class EmailVerifyViews(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = CustomUser.objects.get(pk=payload['user_id'])

            if not user.is_token_valid():
                return Response({"response": "Token has expired"}, status=status.HTTP_403_FORBIDDEN)

            if user:
                user.email_verified = True
                user.save()
                return Response({'response': "Email has been verified successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"response": "Invalid user ID"}, status=status.HTTP_403_FORBIDDEN)

        except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist):
            return Response({"response": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'response': f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#! Define a view to handle forget password requests
class ForgetPasswordViews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        email_error = validation_email(email)
        if email_error:
            return Response(email_error, status=status.HTTP_403_FORBIDDEN)

        try:
            user = CustomUser.objects.filter(email=email).first()
            if user:
                token = generate_verification_token(user.pk)
                password_reset_link = f"{settings.FRONTEND_URL}/reset_password/?token={token}"

                send_mail(
                    'Password Reset Request',
                    f"Here is your password reset link: {password_reset_link}",
                    settings.EMAIL_HOST_USER,
                    [email],
                )
                return Response({'response': "Password reset link has been sent"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)



#! Define a view to handle password reset confirmation
class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        new_password = data.get('password', None)
        token = data.get('token', None)

        if not new_password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

        password_error = validation_password(new_password)
        if password_error:
            return Response(password_error, status=status.HTTP_403_FORBIDDEN)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = CustomUser.objects.get(pk=payload['user_id'])

        except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist):
            return Response({"response": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

        if user:
            user.set_password(new_password)
            user.save()
            return Response({'response': "Password has been reset successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"response": "Invalid user ID"}, status=status.HTTP_403_FORBIDDEN)


#! Define a view to read user profile 
class ProfileRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            pass
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ProfileSerializers(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
#! Define a view to create user profile
class ProfileCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
             # Check if the profile already exists for the logged-in user
            if Profile.objects.filter(user=request.user).exists():
                return Response({'error': 'Profile already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProfileSerializers(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
           
#! Define a view to update user profile
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = ProfileSerializers(profile, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                 return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        