from rest_framework import permissions
from .models import Restaurant, InputtedWaittime, AppUser
from django.utils import timezone

relevant_history = 30 # minutes
point_scale = 10

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class IsOwnerOrReadOnly():
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj == request.user

    
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