from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework.authtoken import views as authviews

router = routers.DefaultRouter()
router.register(r'restaurant', views.RestaurantViewSet)
router.register(r'appuser', views.AppUserViewSet)
router.register(r'address', views.AddressViewSet)
router.register(r'inputtedwaittimes', views.InputtedWaittimeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("average_time/<int:restaurant_id>", views.average_wait_time, name = "average_wait_time"),
    path("get_credibility/<int:user_id>", views.return_credibility, name="get_credibility"),
    path('api-auth/', include('rest_framework.urls')),
    path('user_points/<int:days_ago>', views.user_points, name="user_points"),
    path('api-token-auth/', views.CustomAuthToken.as_view())
]