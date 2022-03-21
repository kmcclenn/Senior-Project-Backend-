from django.db import models
from django.contrib.auth.models import AbstractUser
from address.models import AddressField
from django.core.validators import RegexValidator

class AppUser(AbstractUser):
    pass

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=64)
    address = AddressField(on_delete = models.CASCADE, default = None)
    website = models.URLField(blank=True)
    yelp_page = models.URLField(blank=True)
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, blank=True)

    def __str__(self): 
        return self.name

