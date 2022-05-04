from ctypes import addressof
from .models import Restaurant, AppUser
from address.models import Address
from rest_framework import serializers

class RestaurantSerializer(serializers.ModelSerializer):
    address = serializers.StringRelatedField(many=False)
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'website', 'yelp_page', 'phone_number']

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'credibility_rating', 'points']

class AddressSerializer(serializers.ModelSerializer):
    locality = serializers.StringRelatedField(many=False)
    class Meta:
        model = Address
        fields = ['id', 'raw', 'street_number', 'route', 'locality']
