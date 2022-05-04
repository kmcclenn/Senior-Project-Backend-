
from django.shortcuts import render
from .models import InputtedWaittime, Restaurant, AppUser
from address.models import Address
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from rest_framework.response import Response
from .serializer import RestaurantSerializer, AppUserSerializer, AddressSerializer, InputtedWaittimeSerializer
# from functools import wraps
# import jwt
from django.http import JsonResponse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
    for user in AppUser.objects.all():
        Token.objects.get_or_create(user=user)# if user doesn't have token, create token.


# for user in AppUser.objects.all():
#     Token.objects.get_or_create(user=user)


# Create your views here.

# FBVs - these will do the calcuations
@api_view(['GET'])
def average_wait_time(request, restaurant_id):
    farthest_history_where_wait_times_are_relevant = 30 # minutes
    farthest_history_where_wait_times_are_relevant_seconds = farthest_history_where_wait_times_are_relevant*60
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
        
        if ((timezone.now() - most_recent_time).total_seconds() < farthest_history_where_wait_times_are_relevant_seconds):
            if input.wait_length is not None:
                wait_lengths.append(input.wait_length)
            else:
                wait_length = input.seated_time - input.arrival_time
                wait_length_in_s = wait_length.total_seconds()
                wait_lengths.append(wait_length_in_s)

        average_wait_times = sum(wait_lengths)/len(wait_lengths)
    

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