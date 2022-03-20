from django.db import models

class User(models.User):
    pass

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=64)

    #def __str__(self):
        #return self.name

