
from django.shortcuts import render
from .models import InputtedWaittime, Restaurant, AppUser
from address.models import Address
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from django.utils import timezone
from rest_framework.response import Response
from .serializer import RestaurantSerializer, AppUserSerializer, AddressSerializer, InputtedWaittimeSerializer
# from functools import wraps
# import jwt
from django.http import JsonResponse
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from . import constants


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
    for user in AppUser.objects.all():
        Token.objects.get_or_create(user=user)# if user doesn't have token, create token.

@receiver(pre_save, sender=InputtedWaittime)
def add_accuracy_and_points(sender, instance=None, **kwargs):


    input_time = instance.wait_length
    average_wait_times = get_average_wait_time(instance.restaurant.id)
    if not average_wait_times:
        accuracy = 1
    else:
        accuracy = 1 - (abs(average_wait_times - input_time)/average_wait_times)
        if accuracy < 0:
            accuracy = 0

    instance.accuracy = accuracy

    instance.points = constants.point_scale * accuracy
    ## instance.save() - not sure if needed

    #get instance wait time
    # use average wait time function and/or API to get average wait time
    # compare the two to get credibility
    # use credibility and multiply it by a certain factor(10) to get points
# for user in AppUser.objects.all():
#     Token.objects.get_or_create(user=user)


# Create your views here.
def get_average_wait_time(restaurant_id): ## need to make weighted average
    relevant_history_seconds = constants.relevant_history*60
    restaurant = Restaurant.objects.get(id=restaurant_id)
    ##restaurant_serializer = RestaurantSerializer(restaurant)
    restaurant_wait_time_inputs = InputtedWaittime.objects.filter(restaurant=restaurant)

    wait_lengths = []
    average_wait_times = None
    for input in restaurant_wait_time_inputs:
        if input.arrival_time is not None:
            most_recent_time = input.arrival_time
        else:
            most_recent_time = input.post_time
        
        if ((timezone.now() - most_recent_time).total_seconds() < relevant_history_seconds):
            reporting_user = AppUser.objects.get(id = input.reporting_user.id)

            accuracies = []
            for report in InputtedWaittime.objects.filter(reporting_user = reporting_user):
                accuracies.append(report.accuracy)
            credibility = sum(accuracies)/len(accuracies)

            if input.wait_length is not None:
                wait_lengths.append(input.wait_length * 60 * credibility)
            else:
                wait_length = input.seated_time - input.arrival_time
                wait_length_in_s = wait_length.total_seconds()
                wait_lengths.append(wait_length_in_s * credibility)

    if len(average_wait_times) == 0:
        return None
    average_wait_times = sum(wait_lengths)/len(wait_lengths)
    return average_wait_times / 60 # to put it back in minutes
    
     # copy function from below
# FBVs - these will do the calcuations
@api_view(['GET'])
def average_wait_time(request, restaurant_id):
    
    average_wait_times = get_average_wait_time(restaurant_id=restaurant_id)
    if not average_wait_times:
        return Response({'error': 'not enough data to generate average'})

    ##restaurant_wait_time_inputs_serializer = InputtedWaittimeSerializer(restaurant_wait_time_inputs, many=True)
    return Response({'average_waittime_within_30_minutes': average_wait_times})
   

# CBVs - these just return the basic data from the models
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

class AppUserViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer
    permission_classes = [permissions.IsAuthenticated]

class InputtedWaittimeViewSet(viewsets.ModelViewSet):
    queryset = InputtedWaittime.objects.all()
    serializer_class = InputtedWaittimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # @action(detail=True, methods=['post'])
    # def set_waittime(self, request, pk=None):



class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]


# def get_token_auth_header(request):
#     """Obtains the Access Token from the Authorization Header
#     """
#     auth = request.META.get("HTTP_AUTHORIZATION", None)
#     parts = auth.split()
#     token = parts[1]

#     return token

# def requires_scope(required_scope):
#     """Determines if the required scope is present in the Access Token
#     Args:
#         required_scope (str): The scope required to access the resource
#     """
#     def require_scope(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             token = get_token_auth_header(args[0])
#             decoded = jwt.decode(token, verify=False)
#             if decoded.get("scope"):
#                 token_scopes = decoded["scope"].split()
#                 for token_scope in token_scopes:
#                     if token_scope == required_scope:
#                         return f(*args, **kwargs)
#             response = JsonResponse({'message': 'You don\'t have access to this resource'})
#             response.status_code = 403
#             return response
#         return decorated
#     return require_scope