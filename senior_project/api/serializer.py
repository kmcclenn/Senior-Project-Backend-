from ctypes import addressof
from .models import Restaurant, AppUser, InputtedWaittimes
from address.models import Address
from rest_framework import serializers

class RestaurantSerializer(serializers.ModelSerializer):
    address = serializers.StringRelatedField(many=False)
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'website', 'yelp_page', 'phone_number', 'user_who_created', 'is_active', 'created_time', 'logo_url']


class InputtedWaittimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputtedWaittimes
        fields = ['restaurant', 'wait_length', 'reporting_user', 'accuracy', 'point_value', 'post_time', 'arrival_time', 'seated_time']

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'credibility_rating', 'points']

class AddressSerializer(serializers.ModelSerializer):
    locality = serializers.StringRelatedField(many=False)
    class Meta:
        model = Address
        fields = ['id', 'raw', 'street_number', 'route', 'locality']
