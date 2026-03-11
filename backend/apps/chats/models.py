from django.db import models

# Chat room model
class Room(models.Model):
    user_1 = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='user_1')
    user_2 = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='user_2')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room({self.user_1} & {self.user_2})"
    
# Message model
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    content = models.TextField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"