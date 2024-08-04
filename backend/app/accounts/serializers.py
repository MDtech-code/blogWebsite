
#! Importing DRF serializers for object serialization and deserialization.
from rest_framework import serializers
#! CustomUser model import to extend default User model with additional fields.
from .models import CustomUser
#! authenticate method to verify user credentials during login.
from django.contrib.auth import authenticate
#! Utility function to generate a verification token for email confirmation.
from app.accounts.utils.generate_Token import generate_verification_token
#! timezone from Django utils for time-related operations, such as setting expiry times for tokens.
from django.utils import timezone
#! datetime module for handling date and time objects.
import datetime
#! settings from Django conf to access project settings, like token expiry time.
from django.conf import settings
#! send_mail function to send emails, such as verification and password reset emails.
from django.core.mail import send_mail
#! Form validation utilities to ensure usernames, emails, and passwords meet the project's criteria.
from app.accounts.utils.form_validation import validation_username,validation_email,validation_password


class CustomUserSerializers(serializers.ModelSerializer):
    #! Meta class holds configuration for the serializer
    class Meta:
        #! Specifies the model to be serialized
        model = CustomUser
        #! Fields of the model to be included in the serialized output
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'email_verified']
        #! Additional keyword arguments for the serializer fields
        extra_kwargs = {
            #! Sets the password field to write-only to prevent it from being read with the serialized data
            'password': {'write_only': True}
        }
        
    #! Validates the username to ensure it meets certain criteria (e.g., uniqueness)
    def validate_username(self, value):
        #! Add custom validation logic here
         #! Use your custom validation function
        username_validation_error = validation_username(value)
        if username_validation_error:
            raise serializers.ValidationError(username_validation_error['response'])
        
       #! Check if the username already exists.
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    #! Validates the email to ensure it meets certain criteria (e.g., format, uniqueness)
    def validate_email(self, value):
        #! Add custom validation logic here
        email_validation_error = validation_email(value)
        if email_validation_error:
            raise serializers.ValidationError(email_validation_error['response']) 
        #!Check if the email already exists.
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    #! Validates the password to ensure it meets certain criteria (e.g., strength)
    def validate_password(self, value):
        #! Add custom validation logic here
        password_validation_error = validation_password(value)
        if password_validation_error:
            raise serializers.ValidationError(password_validation_error['response'])
        return value

    #! Overrides the create method to include additional processing during user creation
    def create(self, validated_data):
        #! Creates a new CustomUser instance with the validated data
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        #! Sets the user's password using the set_password method to handle hashing
        user.set_password(validated_data['password'])
        user.save()

        #! Generate a new verification token for the user
        token = generate_verification_token(user.pk)
        #! For debugging purposes, print the token to the console
        print(token)
        #! Uncomment the next line to save the token to the database if needed
        #! user.verification_token = token

        #! Set the token creation time to the current time
        user.token_created_at = timezone.now()
        #! Set the token expiry time to 1 minute from the current time
        user.token_expiry_time = timezone.now() + datetime.timedelta(minutes=1)

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

        #! Return the created user instance
        return user
    


class LoginSerializers(serializers.Serializer):
    #! Define a username field
    username = serializers.CharField()
    #! Define a password field, set to write_only to ensure it is not readable in the response
    password = serializers.CharField(write_only=True)

    #! The validate method is where you define your validation logic
    def validate(self, data):
        #! Retrieve the username and password from the data passed to the serializer
        username = data.get('username')
        password = data.get('password')

        try:
            #! Attempt to retrieve the user with the given username
            user = CustomUser.objects.get(username=username)
            #! Use Django's authenticate method to verify the username and password
            user = authenticate(username=username, password=password)
        
            #! If authentication fails, raise a validation error
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            #! If authentication is successful, add the user object to the data
            data['user'] = user
            return data
        
        #! If no user with the given username exists, raise a validation error
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')


        
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['id','username','email','gender','age','number','address','image']
        

        

