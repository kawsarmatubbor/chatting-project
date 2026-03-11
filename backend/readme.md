# Chatting-project backend with Django, Channels, Redis, and Daphne

This is a **real-time chat application** built using Django, Django REST Framework, Django Channels, Redis, and Daphne. Users can chat privately in rooms.

---

## 1. Project Setup

1. Create a Django project:

```bash
django-admin startproject backend
cd backend
```

2. Create the chat app:

```bash
python manage.py startapp chats
```

---

## 2. Models

`chats/models.py`:

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Room(models.Model):
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_user_1')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_user_2')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

## 3. Serializers

`chats/serializers.py`:

```python
from rest_framework import serializers
from .models import Room, Message

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
```

---

## 4. Views

`chats/views.py`:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer

class RoomViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(Q(user_1=request.user) | Q(user_2=request.user))
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class MessageViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        messages = Message.objects.filter(room_id=room_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
```

---

## 5. URLs

`chats/urls.py`:

```python
from django.urls import path
from .views import RoomViewSet, MessageViewSet

urlpatterns = [
    path('rooms/', RoomViewSet.as_view(), name='rooms'),
    path('rooms/<int:room_id>/messages/', MessageViewSet.as_view(), name='messages'),
]
```

Include in project `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('api/', include('chats.urls')),
]
```

---

## 6. Install Channels & Redis

```bash
pip install channels channels_redis
```

Start Redis server:

```bash
redis-server
```

---

## 7. Django Settings (`settings.py`)

```python
INSTALLED_APPS = [
    ...
    'channels',
    'chats',
]

ASGI_APPLICATION = 'backend.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

---

## 8. Consumers

`chats/consumers.py`:

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user']

        await sync_to_async(Message.objects.create)(room_id=self.room_id, sender=user, content=message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user']
        }))
```

---

## 9. Routing

`chats/routing.py`:

```python
from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),
]
```

`backend/routing.py`:

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chats.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(chats.routing.websocket_urlpatterns)
    ),
})
```

---

## 10. Update `asgi.py`

```python
import os
from channels.routing import get_default_application
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
application = get_default_application()
```

---

## 11. Install Daphne & Run Project

```bash
pip install daphne
daphne backend.asgi:application
```

---

## 12. Testing

- REST endpoints: `/api/rooms/` and `/api/rooms/<id>/messages/`
- WebSocket: `ws://127.0.0.1:8000/ws/chat/<room_id>/`

---

## 13. Optional: Superuser & Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
