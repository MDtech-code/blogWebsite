
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    image=models.ImageField(upload_to='Profile_img/',null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='Gender',null=True)
    age = models.IntegerField(verbose_name='Age',null=True,blank=True)
    address = models.TextField(verbose_name='Address',blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    number = models.CharField(validators=[phone_regex], max_length=20, verbose_name='Phone number',null=True)
    email_verified=models.BooleanField(default=False)
    token_created_at = models.DateTimeField(null=True, blank=True)
    token_expiry_time = models.DateTimeField(null=True, blank=True)
    updated=models.DateTimeField(auto_now=True,null=True)
    created=models.DateField(auto_now_add=True,null=True)

    def is_token_valid(self):
        if self.token_created_at and self.token_expiry_time:
            return timezone.now() < self.token_expiry_time
        return False

    
# Create your models here.




    
    