from django.shortcuts import render
from .models import Restaurant
from rest_framework import viewsets, permissions
from .serializer import RestaurantSerializer

# Create your views here.
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]
    