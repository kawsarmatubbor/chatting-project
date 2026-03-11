import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Message


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        allowed = await self.is_user_allowed()

        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')

        if not message:
            return

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.get_display_name()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user']
        }))

    def get_display_name(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name if full_name else self.user.email

    @sync_to_async
    def is_user_allowed(self):
        try:
            room = Room.objects.select_related("user_1", "user_2").get(id=self.room_id)
            return self.user == room.user_1 or self.user == room.user_2
        except Room.DoesNotExist:
            return False

    @sync_to_async
    def save_message(self, message):
        room = Room.objects.get(id=self.room_id)
        Message.objects.create(
            room=room,
            sender=self.user,
            content=message
        )