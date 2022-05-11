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
    restaurant = serializers.PrimaryKeyRelatedField(many=False, queryset=Restaurant.objects.all(), default=None)
    reporting_user = serializers.PrimaryKeyRelatedField(many=False, queryset=AppUser.objects.all(), default=None)
    class Meta:
        model = InputtedWaittime
        fields = ['id', 'restaurant', 'wait_length', 'reporting_user', 'accuracy', 'point_value', 'post_time', 'arrival_time', 'seated_time']
        depth = 1 # makes the restaurant and reporting user foreign keys actually represented instead of just their pks
        read_only_fields = ('id','accuracy','point_value','post_time')

    # def to_representation(self, value):
    #     self.fields['restaurant'] =  RestaurantSerializer()
    #     self.fields['reporting_user'] = AppUserSerializer()
    #     return super().to_representation(value)

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, validated_data):
        user = AppUser(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class AddressSerializer(serializers.ModelSerializer):
    locality = serializers.StringRelatedField(many=False)
    class Meta:
        model = Address
        fields = ['id', 'raw', 'street_number', 'route', 'locality']
