from django.db import models
from django.contrib.auth.models import AbstractUser
from address.models import AddressField
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import datetime

class AppUser(AbstractUser):
    pass

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=64)
    address = AddressField(on_delete = models.CASCADE, default = None)
    website = models.URLField(blank=True, null=True)
    yelp_page = models.URLField(blank=True, null=True)
    user_who_created = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True, related_name="restaurantscreated")
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, blank=True)
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    logo_url = models.URLField(blank=True, null=True) 

    def __str__(self): 
        return self.name



class InputtedWaittimes(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="waittimes")
    wait_length = models.IntegerField(null=True, blank=True) # either have direct wait length or sitting time minus arrival time
    reporting_user = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True, related_name="inputs")
    accuracy = models.FloatField()
    point_value = models.IntegerField()  
    post_time = models.DateTimeField(auto_now_add=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    seated_time = models.DateTimeField(null=True, blank=True)


