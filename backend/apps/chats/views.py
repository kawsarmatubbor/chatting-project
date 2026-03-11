from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from apps.accounts.models import User
from .models import Room
from .serializers import RoomSerializer, RoomDetailSerializer


class RoomViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(
            Q(user_1=request.user) | Q(user_2=request.user)
        )
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_2_id = request.data.get("user_2")

        if not user_2_id:
            return Response(
                {"error": "user_2 is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_1 = request.user
        try:
            user_2 = User.objects.get(id=user_2_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        room = Room.objects.filter(
            Q(user_1=user_1, user_2=user_2) |
            Q(user_1=user_2, user_2=user_1)
        ).first()

        if room:
            serializer = RoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)

        room = Room.objects.create(user_1=user_1, user_2=user_2)
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class RoomDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        room = get_object_or_404(Room, id=id)
        
        if request.user != room.user_1 and request.user != room.user_2:
            return Response({"detail": "You do not have permission to view this room."},
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoomDetailSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)