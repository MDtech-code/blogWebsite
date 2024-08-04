
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
from .models import CustomUser
from .serializers import CustomUserSerializers, LoginSerializers,UserProfileSerializer
from app.accounts.utils.generate_Token import generate_verification_token
from app.accounts.utils.form_validation import validation_email, validation_password

#! Standard library imports
import datetime

class CsrfTokenViews(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        #! Retrieves a CSRF token for the given request
        csrfToken = get_token(request) 
        #! Returns the CSRF token in the response
        return Response({'csrfToken': csrfToken})
'''
#! this view help to send csrf token to frontend
@api_view(['GET'])
def csrf_token_views(request):
    try:
        csrf_token = get_token(request)
        response=Response({'csrfToken': csrf_token})
        response.set_cookie('csrftoken',csrf_token,max_age=31449600,secure=True,httponly=True,samesite='None')
        return response
    except Exception as e:
        return Response({'responseErrorMessage': str(e)}, status=500)
'''

    

#! SignupViews is a class-based view that handles user registration.
class SignupViews(APIView):
    permission_classes = [AllowAny]  #! The post method responds to HTTP POST requests.
    def post(self, request):
        #! request.data contains the data sent in the POST request.
        data = request.data
        
        #! CustomUserSerializers is used to validate and serialize the data.
        serializers = CustomUserSerializers(data=data)
        
        #! is_valid() checks if the data provided is valid according to the serializer.
        if serializers.is_valid():
            #! If the data is valid, save the new user to the database.
            serializers.save()
            
            #! Return a success response with a message and HTTP 201 status code.
            return Response({'Response': 'user created successfully'}, status=status.HTTP_201_CREATED)
        
        #! If the data is not valid, return an error response with the errors and HTTP 400 status code.
        return Response({'ResponseError': serializers.errors}, status=status.HTTP_400_BAD_REQUEST)



#! Define a view to handle send email verification link
class SendEmailVerificationView(APIView):
    #permission_classes = [IsAuthenticated] #! Define the POST method, as this view will be used to send a verification email
    def post(self, request):
        #! Retrieve the current user from the request
        user = request.user
        #! Check if the user's email is not already verified
        if not user.email_verified:
            try:
                #! Generate a new verification token for the user
                token = generate_verification_token(user.pk)
               

                #! Set the token creation time to the current time
                user.token_created_at = timezone.now()
                #! Set the token expiry time to 1 minute from now
                user.token_expiry_time = timezone.now() + datetime.timedelta(minutes=1)
                #! Save the user's updated information
                user.save()

                #! Construct the verification link with the generated token
                verification_link = f"{settings.FRONTEND_URL}/verify_email/?token={token}"
                #! Send an email to the user with the verification link
                send_mail(
                    'Email Verification Request',
                    f"Here is your email verification link: {verification_link}",
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                #! Return a success response indicating the email was sent
                return Response({'message': 'Verification email sent successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                #! If an error occurs, log the error or send it back as a response
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            #! If the user's email is already verified, return a bad request response
            return Response({'message': 'Email is already verified'}, status=status.HTTP_400_BAD_REQUEST)

#! define a view to handle the email verifcation
class EmailVerifyViews(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        #! Retrieve the token from the query parameters of the request URL
        token = request.query_params.get('token')
        
        try:
            #! Decode the JWT token using the SECRET_KEY and HS256 algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            #! Retrieve the user associated with the user_id in the payload
            user = CustomUser.objects.get(pk=payload['user_id'])
            
            #! Check if the token is still valid
            if not user.is_token_valid():
                #! If the token has expired, return a 403 Forbidden response
                return Response({"response": "Token has expired"}, status=status.HTTP_403_FORBIDDEN)
            
            #! If the token is valid and the user exists
            if user:
                #! Set the email_verified field to True
                user.email_verified = True
                  #! Clear the token after successful verification
                #!user.verification_token = None
                #! Save the changes to the user object
                user.save()
                #! Return a 200 OK response indicating successful email verification
                return Response({'response': "Email has been verified successfully"}, status=status.HTTP_200_OK)
            else:
                #! If the user does not exist, return a 403 Forbidden response
                return Response({"response": "Invalid user ID"}, status=status.HTTP_403_FORBIDDEN)
        
        #! Handle specific exceptions related to JWT token errors
        except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist):
            #! Return a 403 Forbidden response for invalid tokens
            return Response({"response": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)
        
        #! Handle any other exceptions that may occur
        except Exception as e:
            #! Return a 500 Internal Server Error response with the exception message
            return Response({'response': f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
#! LoginViews is a class-based view that handles user login.
class LoginViews(APIView):
    permission_classes = [AllowAny]
    #! The post method responds to HTTP POST requests.
    def post(self, request):
        #! request.data contains the data sent in the POST request.
        data = request.data
        
        #! LoginSerializers is used to validate and deserialize the data.
        serializers = LoginSerializers(data=data)
        
        #! is_valid() checks if the data provided is valid according to the serializer.
        if serializers.is_valid():
            #! If the data is valid, retrieve the user from the validated data.
            user = serializers.validated_data['user']
            
            #! Log the user in using Django's login function.
            login(request, user)
            
             #! Create tokens using SimpleJWT
            refresh = RefreshToken.for_user(user)
            print(str(refresh))
            response=  Response({
                'access': str(refresh.access_token),
                'loginuser': user.username,
                'response': 'Login successful',
            }, status=status.HTTP_200_OK)
            response.set_cookie('refresh_token', str(refresh), httponly=True, samesite='None')
            #! Return a success response with a message.
            return response
        
        #! If the data is not valid, return an error response with the message 'Invalid Credentials' and HTTP 400 status code.
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
#! @method_decorator(csrf_exempt, name='dispatch')

@method_decorator(csrf_exempt, name='dispatch')
class ForgetPasswordViews(APIView):
    permission_classes = [IsAuthenticated]
    #! POST method to handle the password reset request
    def post(self, request, *args, **kwargs):
        #! Retrieve the email from the request data
        email = request.data.get('email', None)
        #! If email is not provided, return an error response
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        #! Validate the email using a custom validation function
        email_error = validation_email(email)
        #! If there's an error in validation, return a forbidden response
        if email_error:
            return Response(email_error, status=status.HTTP_403_FORBIDDEN)
        
        try:
            #! Attempt to retrieve the user with the provided email
            user = CustomUser.objects.filter(email=email).first()
            #! If a user is found
            if user:
                #! Generate a verification token for the user
                token = generate_verification_token(user.pk)
                #! Create a password reset link with the token
                password_reset_link = f"{settings.FRONTEND_URL}/reset_password/?token={token}"
                
                #! Send an email to the user with the password reset link
                send_mail(
                    'Password Reset Request',
                    f"Here is your password reset link: {password_reset_link}",
                    settings.EMAIL_HOST_USER,
                    [email],
                )
                #! Return a success response indicating the email has been sent
                return Response({'response': "Password reset link has been sent"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            #! If no user is found with the provided email, return a not found response
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)



@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(APIView):
    #! POST method to handle the password reset confirmation
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        #! Retrieve the data from the request
        data = request.data
        #! Extract the new password and token from the data
        new_password = data.get('password', None)
        token = data.get('token', None)
        
        #! If the new password is not provided, return an error response
        if not new_password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        #! Validate the new password using a custom validation function
        password_error = validation_password(new_password)
        #! If there's an error in validation, return a forbidden response
        if password_error:
            return Response(password_error, status=status.HTTP_403_FORBIDDEN)
        
        try:
            #! Decode the token using JWT to get the user's ID
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            #! Retrieve the user based on the ID found in the token
            user = CustomUser.objects.get(pk=payload['user_id'])
            
        except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist):
            #! If the token is invalid or expired, or the user does not exist, return an invalid token response
            return Response({"response": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)
        
        #! If the user is found
        if user:
            #! Set the new password for the user
            user.set_password(new_password)
            #! Save the user object to update the password in the database
            user.save()
            #! Return a success response indicating the password has been reset
            return Response({'response': "Password has been reset successfully"}, status=status.HTTP_200_OK)
        else:
            #! If the user object is not found, return an invalid user ID response
            return Response({"response": "Invalid user ID"}, status=status.HTTP_403_FORBIDDEN)




#! LogoutViews is a class-based view that handles user logout.
class LogoutViews(APIView):
    #! The post method responds to HTTP POST requests.
    permission_classes = [IsAuthenticated]
    def post(self, request):
        #! logout() is a Django function that logs the user out, removing the user's ID from the session.
        logout(request)
        
        #! Return a success response with a message and HTTP 200 status code.
        return Response({'Response': 'Logout successful'}, status=status.HTTP_200_OK)





class UserProfileUpdateView(APIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user