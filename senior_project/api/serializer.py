from ctypes import addressof
from .models import Restaurant, AppUser, InputtedWaittime
from address.models import Address
from rest_framework import serializers

class RestaurantSerializer(serializers.ModelSerializer):
    address = serializers.StringRelatedField(many=False)
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'website', 'yelp_page', 'phone_number', 'user_who_created', 'is_active', 'created_time', 'logo_url']

class InputtedWaittimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputtedWaittime
        fields = ['restaurant', 'wait_length', 'reporting_user', 'accuracy', 'point_value', 'post_time', 'arrival_time', 'seated_time']
        depth = 1 # makes the restaurant and reporting user foreign keys actually represented instead of just their pks

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'credibility_rating', 'points']

class AddressSerializer(serializers.ModelSerializer):
    locality = serializers.StringRelatedField(many=False)
    class Meta:
        model = Address
        fields = ['id', 'raw', 'street_number', 'route', 'locality']
