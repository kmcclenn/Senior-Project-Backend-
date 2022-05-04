from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework.authtoken import views as authviews

router = routers.DefaultRouter()
router.register(r'restaurant', views.RestaurantViewSet)
router.register(r'appuser', views.AppUserViewSet)
router.register(r'address', views.AddressViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', authviews.obtain_auth_token)
]