from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
# router.register(
#     r'^users/(?P<user_id>\d+)/subscribe',
#     SubscribeViewSet,
#     basename='subscribe'
# )

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
