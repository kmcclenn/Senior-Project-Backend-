from ctypes import addressof
from wsgiref import validate
from .models import Restaurant, AppUser, InputtedWaittime, RestaurantAddress
#from address.models import Address, Locality
from rest_framework import serializers
from . import utils
from rest_framework.response import Response
from django.utils import timezone

class RestaurantSerializer(serializers.ModelSerializer):
    address = serializers.SlugRelatedField(many=False, slug_field = 'raw', queryset=RestaurantAddress.objects.all())
    user_who_created = serializers.PrimaryKeyRelatedField(many=False, queryset=AppUser.objects.all(), default=None)
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

    ## makes sure one user cannot input more than once every 30 mins
    def create(self, validated_data):
        user = AppUser.objects.get(pk=validated_data['reporting_user'].id)
        user_inputs = InputtedWaittime.objects.filter(reporting_user = user).filter(restaurant = validated_data['restaurant'])
        timely_user_inputs = []
        for input in user_inputs:
            if input.arrival_time is not None:
                most_recent_time = input.arrival_time
            else:
                most_recent_time = input.post_time
            timely_user_inputs.append([input, most_recent_time])
        print("pre-sorted: ")
        print(timely_user_inputs)
        # creates list of inputs and when it was posted and sorts it according to post time
        timely_user_inputs.sort(key=lambda item: item[1], reverse=True) 

        try:
            input_recent_time = validated_data['arrival_time']
        except KeyError:
            input_recent_time = timezone.now()
        
        if len(timely_user_inputs) == 0:
            return return_inputted_waittime(validated_data)
        
        print((input_recent_time - timely_user_inputs[0][1]).total_seconds()/60)
        # if the current time minus the previous post time is greater than 30 mins
        # then allow
        # otherwise, raise error
        if (input_recent_time - timely_user_inputs[0][1]).total_seconds() > utils.relevant_history * 60:
            
            return return_inputted_waittime(validated_data)
        else:
            raise serializers.ValidationError("wait to input new time")
            #return Response({'error': f'already inputted time within past {utils.relevant_history} minutes'})

# generic function for returning an inputted wait time object   
def return_inputted_waittime(validated_data):

    try:
        wait_length = validated_data['wait_length']
    except KeyError:
        wait_length = (validated_data['seated_time'] - validated_data['arrival_time']).total_seconds() / 60

    inputted_waittime = InputtedWaittime(restaurant=validated_data['restaurant'],
                    wait_length=wait_length,
                    reporting_user=validated_data['reporting_user'])

    try:
        inputted_waittime.arrival_time = validated_data['arrival_time']
    except KeyError:
        pass
    try:
        inputted_waittime.seated_time = validated_data['seated_time']
    except KeyError:
        pass
    inputted_waittime.save()
    return inputted_waittime


class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False
                }
            }

    # creates user and sets password
    def create(self, validated_data):
        user = AppUser(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantAddress
        fields = ['id', 'raw', 'street', 'city', 'zip', 'state']
    
    # creates address unless already exists
    def create(self, validated_data):
        print("create run")
        address, created = RestaurantAddress.objects.get_or_create(raw = validated_data["raw"], street = validated_data["street"], zip = validated_data["zip"], city = validated_data["city"], state = validated_data["state"])
        address.save()
        return address