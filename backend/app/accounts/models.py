
   
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone

class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    token_created_at = models.DateTimeField(null=True, blank=True)
    token_expiry_time = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateField(auto_now_add=True, null=True)

    def is_token_valid(self):
        if self.token_created_at and self.token_expiry_time:
            return timezone.now() < self.token_expiry_time
        return False

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio=models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='Profile_img/',blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True)
    age = models.IntegerField(null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    number = models.CharField(validators=[phone_regex], max_length=20, null=True)
    facebook_url=models.CharField(max_length=100,null=True, blank=True)
    instagram_url=models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.user.username

