from django.db import models
from django.contrib.auth.models import AbstractUser
from address.models import AddressField

class User(AbstractUser):
    pass

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=64)
    address = AddressField(on_delete = models.CASCADE, default = None)

    #def __str__(self):
        #return self.name

