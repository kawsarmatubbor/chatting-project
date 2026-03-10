from django.urls import path
from .views import RoomViewSet

urlpatterns = [
    path('rooms/', RoomViewSet.as_view(), name='rooms'),
]