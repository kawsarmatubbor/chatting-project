from django.urls import path
from .views import RoomViewSet, RoomDetailView

urlpatterns = [
    path('rooms/', RoomViewSet.as_view(), name='rooms'),
    path('rooms/<int:id>/', RoomDetailView.as_view(), name='room-detail'),
]