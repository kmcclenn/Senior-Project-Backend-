
from rest_framework import permissions
from .models import Restaurant, InputtedWaittime, AppUser
from django.utils import timezone

relevant_history = 30 # minutes
point_scale = 10
time_constant = 0.17

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id ## if both are none, then it works too - so works when creating new user.

class MustBeAdminToChange(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == "PUT" and request.user.is_staff:
            return True
        return super().has_object_permission(self, request, view, obj)

def get_credibility(user_id):
    reporting_user = AppUser.objects.get(id = user_id)

    accuracies = []
    for report in InputtedWaittime.objects.filter(reporting_user = reporting_user):
        accuracies.append(report.accuracy)
    if len(accuracies) == 0:
        credibility = 1
    else:
        credibility = sum(accuracies)/len(accuracies)
    return credibility

def get_average_wait_time(restaurant_id): ## need to make weighted average
    relevant_history_seconds = relevant_history*60
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
            

            credibility = get_credibility(input.reporting_user.id)

            if input.wait_length is not None:
                wait_lengths.append([float(input.wait_length) * 60, credibility])
            # elif input.seated_time is not None and input.arrival_time is not None:
            #     wait_length = input.seated_time - input.arrival_time
            #     wait_length_in_s = wait_length.total_seconds()
            #     wait_lengths.append([float(wait_length_in_s), credibility])
            else:
                return None

    if len(wait_lengths) == 0:
        return None

    total_credibility = 0
    for pair in wait_lengths:
        total_credibility += pair[1]

    average_wait_times = 0
    for pair in wait_lengths:
        weight = pair[1]/total_credibility
        average_wait_times += (weight * pair[0])
    
    return [average_wait_times / 60, wait_lengths] # to put it back in minutes


# def get_restaurant_queryset():
#     restaurants = Restaurant.objects.filter(is_approved = True)
#     restaurant_wait_time_list = []
#     for restaurant in restaurants:
#         wait_time = get_average_wait_time(restaurant.id)
#         if wait_time == None:
#             wait_time = 10000 ## high number
#         restaurant_wait_time_list.append([restaurant, wait_time])
#     restaurant_wait_time_list.sort(key=lambda item: item[1])
#     queryset_list = []
#     for item in restaurant_wait_time_list:
#         queryset_list.append(item[0])
#     return queryset_list