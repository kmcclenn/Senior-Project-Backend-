from django.contrib import admin
from address.models import AddressField
from address.forms import AddressWidget
from .models import Restaurant, AppUser, InputtedWaittime
from django import forms
from address.models import Address

# Register your models here.
admin.site.register(AppUser)
admin.site.register(InputtedWaittime)

class RestaurantModel(Restaurant):

    class Meta:
        proxy = True

class AddressForm(forms.ModelForm):
    addresses = Address.objects.all()
    
        #convert addresses to tuple.
    #CHOICES = [(item.route, item) for item in addresses]
    
    address = forms.ModelChoiceField(queryset=addresses)



@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    form = AddressForm
