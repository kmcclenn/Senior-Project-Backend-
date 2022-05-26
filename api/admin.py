from django.contrib import admin
from .models import Restaurant, AppUser, InputtedWaittime, RestaurantAddress
from django import forms


# Register your models here.
admin.site.register(AppUser)
admin.site.register(InputtedWaittime)
admin.site.register(RestaurantAddress)


class RestaurantModel(Restaurant):

    class Meta:
        proxy = True

class AddressForm(forms.ModelForm):
    addresses = RestaurantAddress.objects.all()
    
    address = forms.ModelChoiceField(queryset=addresses)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    form = AddressForm
