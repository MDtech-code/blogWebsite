from rest_framework import serializers
from .models import CustomUser,Profile
from django.contrib.auth import authenticate
from app.accounts.utils.generate_Token import generate_verification_token
from django.utils import timezone
import datetime
from django.conf import settings
from django.core.mail import send_mail
from app.accounts.utils.form_validation import validation_username, validation_email, validation_password,validation_bio, validation_image, validation_gender,validation_age, validation_number, validation_facebook_url,validation_instagram_url

#! serializer for signup form 
class CustomUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'email_verified']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_username(self, value):
        username_validation_error = validation_username(value)
        if username_validation_error:
            raise serializers.ValidationError(username_validation_error['response'])

        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        email_validation_error = validation_email(value)
        if email_validation_error:
            raise serializers.ValidationError(email_validation_error['response'])

        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_password(self, value):
        password_validation_error = validation_password(value)
        if password_validation_error:
            raise serializers.ValidationError(password_validation_error['response'])
        return value

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        token = generate_verification_token(user.pk)
        print(token)

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

        return user

#! serializer for login form 

class LoginSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(username=username)
            print(f"User found: {user.username}")

            # Check if email is verified
            if not user.email_verified:
                print("Email not verified. Sending verification email.")
                # Resend verification email
                token = generate_verification_token(user.pk)
                verification_link = f"{settings.FRONTEND_URL}/verify_email/?token={token}"
                send_mail(
                    'Email Verification Request',
                    f"Here is your email verification link: {verification_link}",
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )

                # Update token creation and expiry time
                user.token_created_at = timezone.now()
                user.token_expiry_time = timezone.now() + datetime.timedelta(minutes=30)
                user.save()

                raise serializers.ValidationError('Email not verified. Verification email resent.')

            # Authenticate user
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')

            data['user'] = user
            return data

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')



#! serializers for profile 
class SimpleCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'email']

class ProfileSerializers(serializers.ModelSerializer):
    user = SimpleCustomUserSerializer()

    class Meta:
        model = Profile
        fields = ['id', 'bio', 'image', 'gender', 'age', 'number', 'facebook_url', 'instagram_url', 'user']
    #! validated data function
    def validate_bio(self, value):
        bio_validation_error = validation_bio(value)
        if bio_validation_error:
            raise serializers.ValidationError(bio_validation_error['response'])
        return value

    def validate_image(self, value):
        image_validation_error = validation_image(value)
        if image_validation_error:
            raise serializers.ValidationError(image_validation_error['response'])
        return value

    def validate_gender(self, value):
        gender_validation_error = validation_gender(value)
        if gender_validation_error:
            raise serializers.ValidationError(gender_validation_error['response'])
        return value

    def validate_age(self, value):
        age_validation_error = validation_age(value)
        if age_validation_error:
            raise serializers.ValidationError(age_validation_error['response'])
        return value

    def validate_number(self, value):
        number_validation_error = validation_number(value)
        if number_validation_error:
            raise serializers.ValidationError(number_validation_error['response'])
        return value

    def validate_facebook_url(self, value):
        facebook_url_validation_error = validation_facebook_url(value)
        if facebook_url_validation_error:
            raise serializers.ValidationError(facebook_url_validation_error['response'])
        return value

    def validate_instagram_url(self, value):
        instagram_url_validation_error = validation_instagram_url(value)
        if instagram_url_validation_error:
            raise serializers.ValidationError(instagram_url_validation_error['response'])
        return value

    def create(self, validated_data):
        # Access the current logged-in user
        request = self.context.get('request')
        user = request.user
        
        #! Create and save the Profile instance
        profile = Profile.objects.create(user=user, **validated_data)
        #profile = Profile(
        #    user=user,
        #    bio=validated_data.get('bio', ''),
        #    image=validated_data.get('image', None),
        #    gender=validated_data.get('gender', ''),
        #    age=validated_data.get('age', 0),
        #    number=validated_data.get('number', ''),
        #    facebook_url=validated_data.get('facebook_url', ''),
        #    instagram_url=validated_data.get('instagram_url', '')
        #)
        profile.save()
        return profile

    def update(self, instance, validated_data):
        # Extract user data from validated_data
        #user_data = self.context['request'].data.get('user', None)
        user_data = validated_data.pop('user', None)
        if user_data:
            # Access the related user instance
            user = instance.user
            #! Update user fields with the extracted data
            user.first_name = user_data.get('first_name', user.first_name)

            new_email = user_data.get('email')
            if new_email and new_email != user.email:
                user.email_verified = False
                user.token_created_at=None
                user.token_expiry_time=None
                user.email=new_email
            user.save()
            
            #! Update user fields with the extracted data
            #for attr, value in user_data.items():
            #    setattr(user, attr, value)
            #user.save()
        
        #! Update and save the Profile instance
        #for attr, value in validated_data.items():
        #    setattr(instance, attr, value)
        #!Update profile fields with the validated data
        instance.bio = validated_data.get('bio', instance.bio)
        instance.image = validated_data.get('image', instance.image)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.age = validated_data.get('age', instance.age)
        instance.number = validated_data.get('number', instance.number)
        instance.facebook_url = validated_data.get('facebook_url', instance.facebook_url)
        instance.instagram_url = validated_data.get('instagram_url', instance.instagram_url)
        instance.save()
        return instance
