from django.db import models
from django.contrib.auth.models import AbstractUser
from address.models import AddressField
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class AppUser(AbstractUser):
    credibility_rating = models.FloatField(default=0)
    #points = models.IntegerField(default=0)
    #pass

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=64)
    address = AddressField(on_delete = models.CASCADE, default = None)
    website = models.URLField(blank=True)
    yelp_page = models.URLField(blank=True)
    user_who_created = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True, related_name="restaurantscreated")
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, blank=True)

    def __str__(self): 
        return self.name



class InputtedWaittimes(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="waittimes")
    wait_length = models.IntegerField()
    reporting_user = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True, related_name="inputs")
    accuracy = models.FloatField()
    point_value = models.IntegerField()      

