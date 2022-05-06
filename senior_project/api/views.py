
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
from . import utils


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
    for user in AppUser.objects.all():
        Token.objects.get_or_create(user=user)# if user doesn't have token, create token.

@receiver(pre_save, sender=InputtedWaittime)
def add_accuracy_and_points(sender, instance=None, **kwargs):
    if instance.id is None: # making sure its a new save
        restaurant_wait_time_inputs = InputtedWaittime.objects.filter(restaurant=instance.restaurant)
        most_recent_times = []
        for input in restaurant_wait_time_inputs:
            if input.arrival_time is not None:
                most_recent_time = input.arrival_time
            else:
                most_recent_time = input.post_time
            most_recent_times.append([input.id, most_recent_time])
        most_recent_times.sort(key=lambda pair: pair[1])
        if len(most_recent_times) > 0:

            recent_time = most_recent_times[-1][1]

            
            if instance.arrival_time is not None:
                instance_time = instance.arrival_time
            else:
                instance_time = instance.post_time

            time_difference = (instance_time - recent_time).total_seconds() / 60
            if time_difference > utils.relevant_history:
                time_factor = 0
            else:
                time_factor = (time_difference/utils.relevant_history) * utils.time_constant
        else:
            time_factor = 0
            

        input_time = instance.wait_length
        average_wait_times = utils.get_average_wait_time(instance.restaurant.id)
        if not average_wait_times:
            accuracy = 1
        else:
            accuracy = 1 - (abs(average_wait_times[0] - input_time)/average_wait_times[0])
            accuracy += time_factor
            if accuracy < 0:
                accuracy = 0

        instance.accuracy = accuracy
        instance.point_value = utils.point_scale * accuracy
    else:
        pass

    ## instance.save() - not sure if needed

    #get instance wait time
    # use average wait time function and/or API to get average wait time
    # compare the two to get credibility
    # use credibility and multiply it by a certain factor(10) to get points
# for user in AppUser.objects.all():
#     Token.objects.get_or_create(user=user)


# Create your views here.

    
     
# FBVs - these will do the calcuations
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def return_credibility(request, user_id):
    credibility = utils.get_credibility(user_id)
    return Response({f'user {user_id} credibility': credibility})

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
    ##restaurant_wait_time_inputs_serializer = InputtedWaittimeSerializer(restaurant_wait_time_inputs, many=True)
    # return if list: return Response({'average_waittime_within_30_minutes': ' '.join(str(e) for e in average_wait_times)})
   

# CBVs - these just return the basic data from the models
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [utils.IsAdminOrReadOnly]

class AppUserViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer
    permission_classes = [utils.IsOwnerOrReadOnly]

class InputtedWaittimeViewSet(viewsets.ModelViewSet):
    queryset = InputtedWaittime.objects.all()
    serializer_class = InputtedWaittimeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # @action(detail=True, methods=['post'])
    # def set_waittime(self, request, pk=None):



class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.AllowAny]


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