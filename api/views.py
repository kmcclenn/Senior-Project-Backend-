
from itertools import count
from re import L
from django.shortcuts import render
from . import models
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from django.utils import timezone
from rest_framework.response import Response
from .serializer import RestaurantSerializer, AppUserSerializer, InputtedWaittimeSerializer, AddressSerializer
from django.http import JsonResponse
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from . import utils
from rest_framework.authtoken.views import ObtainAuthToken

# sets token for user if a new user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
    for user in models.AppUser.objects.all():
        Token.objects.get_or_create(user=user)# if user doesn't have token, create token.

# sets the accuracy, points, and wait length for new inputted waittime object
@receiver(pre_save, sender=models.InputtedWaittime)
def add_accuracy_and_points_and_waitlength(sender, instance=None, **kwargs):
    print(vars(instance))
    if instance.id is None: # making sure its a new save
        
        if instance.wait_length is None: # if there is no wait length, then determine it by seated time minus arrival time
            try:
                instance.wait_length = (instance.seated_time - instance.arrival_time).total_seconds() / 60
            except TypeError:
                instance.wait_length = 0
        
        restaurant = models.Restaurant.objects.get(pk=instance.restaurant_id)
        restaurant_wait_time_inputs = models.InputtedWaittime.objects.filter(restaurant=restaurant)
        most_recent_times = []
        # find most accurate time of input (either arrival time or post time)
        for input in restaurant_wait_time_inputs:
            if input.arrival_time is not None:
                most_recent_time = input.arrival_time
            else:
                most_recent_time = input.post_time
            most_recent_times.append([input.id, most_recent_time])
        most_recent_times.sort(key=lambda pair: pair[1])

        if len(most_recent_times) > 0:
            recent_time = most_recent_times[-1][1] # finds most recent input
            if instance.arrival_time is not None:
                instance_time = instance.arrival_time
            else:
                instance_time = instance.post_time

            time_difference = (instance_time - recent_time).total_seconds() / 60
            if time_difference > utils.relevant_history:
                time_factor = 0
            else: # creates a time factor based on how far away input is from previous input
                time_factor = (time_difference/utils.relevant_history) * utils.time_constant
        else:
            time_factor = 0
            
        # finds input time accuracy
        input_time = instance.wait_length
        average_wait_times = utils.get_average_wait_time(instance.restaurant.id)
        if not average_wait_times:
            accuracy = 1
        else:
            if average_wait_times[0] == 0:
                accuracy = input_time/10 if input_time < 10 else 0
            else:
                accuracy = 1 - (abs(average_wait_times[0] - input_time)/average_wait_times[0])
            accuracy += time_factor
            if accuracy < 0:
                accuracy = 0
        
        # adds accuracy which is a sum of the distance from average and the time factor
        instance.accuracy = accuracy
        # adds point value by multiplying accuracy by constant
        instance.point_value = utils.point_scale * accuracy
    else:
        pass

# FBVs - these will do the calcuations

# gets user points
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_points(request, days_ago):

    if days_ago == 0:
        seconds_ago = None
    else:
        seconds_ago = days_ago * 86400


    active_users = models.AppUser.objects.filter(is_active = True)
    user_and_points = []
    for user in active_users:
        reported_wts = models.InputtedWaittime.objects.filter(reporting_user = user)
        total_points = 0
        for wt in reported_wts:
            if wt.arrival_time is not None:
                most_recent_time = wt.arrival_time
            else:
                most_recent_time = wt.post_time

            # adds to total points based on how far ago it is searching
            if seconds_ago is not None and (timezone.now() - most_recent_time).total_seconds() < seconds_ago:
                total_points += wt.point_value
            elif seconds_ago is None:
                total_points += wt.point_value
        user_and_points.append({'id': user.id, 'points': total_points})
    if len(user_and_points) != 0:
        user_and_points = sorted(user_and_points, reverse = True, key=lambda item: item['points'])
    return Response(user_and_points) # returns dict of the user id and their points

# returns the credibility of the user
@api_view(['GET'])
@permission_classes([utils.IsOwner])
def return_credibility(request, user_id):
    credibility = utils.get_credibility(user_id)
    return Response({'id': user_id, 'credibility': credibility})

# returns the wait time of a restaurant along with the list of waittime inputs
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def average_wait_time(request, restaurant_id):
    
    average_wait_time_response = utils.get_average_wait_time(restaurant_id=restaurant_id)
   
    if not average_wait_time_response:
        return Response({'error': 'not enough data to generate average'})
    average_wait_time = average_wait_time_response[0]
    wait_time_list = average_wait_time_response[1] # pre weights
    return Response({'id': restaurant_id,
                    f'average_waittime_within_past_{utils.relevant_history}_minutes': average_wait_time,
                    'wait_list': ', '.join(str(e) for e in wait_time_list)})

# CBVs - these just return the basic data from the models
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = models.Restaurant.objects.filter(is_approved=True)
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AppUserViewSet(viewsets.ModelViewSet):
    queryset = models.AppUser.objects.all()
    serializer_class = AppUserSerializer
    permission_classes = [utils.IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.create(serializer.validated_data)

class InputtedWaittimeViewSet(viewsets.ModelViewSet):
    queryset = models.InputtedWaittime.objects.all()
    serializer_class = InputtedWaittimeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.create(serializer.validated_data)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = models.RestaurantAddress.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [utils.MustBeAdminToChange]

    def perform_create(self, serializer):
        #print(serializer.is_valid())
        if serializer.is_valid():
            #print(serializer.validated_data)
            serializer.create(serializer.validated_data)


# sets custom response when creating token
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': str(user.pk),
        })