from django.db import models
from django.contrib.auth.models import AbstractUser
from address.models import AddressField
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import datetime
from django.utils import timezone

class AppUser(AbstractUser):
    email = models.EmailField(unique=True)

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=64, unique=True)
    address = AddressField(on_delete = models.CASCADE, default = None)
    website = models.URLField(blank=True, null=True)
    yelp_page = models.URLField(blank=True, null=True)
    user_who_created = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True, related_name="restaurantscreated")
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    logo_url = models.URLField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self): 
        return self.name



class InputtedWaittime(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="waittimes")
    # in minutes:
    wait_length = models.IntegerField(null=True, blank=True) # either have direct wait length or sitting time minus arrival time
    reporting_user = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True, related_name="inputs")
    accuracy = models.FloatField(default = 1)
    point_value = models.IntegerField(default = 10)  
    post_time = models.DateTimeField(auto_now_add=True)
    arrival_time = models.DateTimeField(null=True, blank=True, default = timezone.now)
    seated_time = models.DateTimeField(null=True, blank=True)


