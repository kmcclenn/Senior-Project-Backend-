
from rest_framework import permissions
from .models import Restaurant, InputtedWaittime, AppUser
from django.utils import timezone

relevant_history = 30 # minutes
point_scale = 10
time_constant = 0.17

# custom permission
class IsAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff

# custom permission
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id ## if both are none, then it works too - so works when creating new user.

# custom permission that allows anything if authenticated unless method is post, then must be admin
class MustBeAdminToChange(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method != "POST":
            if request.user.is_staff:
                return True
            else:
                return False
        return request.user.is_authenticated

# custom permission
class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.id == view.kwargs['user_id']

 # returns credibility of each user based on their input history
def get_credibility(user_id):
    reporting_user = AppUser.objects.get(id = user_id)

    accuracies = []
    for report in InputtedWaittime.objects.filter(reporting_user = reporting_user):
        accuracies.append(report.accuracy)
    if len(accuracies) == 0:
        credibility = 1
    else:
        credibility = sum(accuracies)/len(accuracies) # average of accuracies
    return credibility

# gets average weight time using weighted average
def get_average_wait_time(restaurant_id):
    relevant_history_seconds = relevant_history*60
    restaurant = Restaurant.objects.get(id=restaurant_id) # gets restaurant object
    restaurant_wait_time_inputs = InputtedWaittime.objects.filter(restaurant=restaurant) # gets inputs for restaurant

    wait_lengths = []
    average_wait_times = None
    for input in restaurant_wait_time_inputs: # loops through inputs to find the ones within relevant history
        if input.arrival_time is not None:
            most_recent_time = input.arrival_time
        else:
            most_recent_time = input.post_time
        
        # if the input is in relevant history, add it and the users credibility to a list
        if ((timezone.now() - most_recent_time).total_seconds() < relevant_history_seconds):
            credibility = get_credibility(input.reporting_user.id)
            if input.wait_length is not None:
                wait_lengths.append([float(input.wait_length) * 60, credibility])
            else:
                return None

    if len(wait_lengths) == 0:
        return None

    # find total credibility for weighted average
    total_credibility = 0
    for pair in wait_lengths:
        total_credibility += pair[1]

    # loop through wait lengths and find weighted average of weight lengths based on their user's credibility
    average_wait_times = 0
    for pair in wait_lengths:
        weight = pair[1]/total_credibility
        average_wait_times += (weight * pair[0])
    
    return [average_wait_times / 60, wait_lengths] # to put it back in minutes
