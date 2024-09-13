from django.db import models
from django.user.models import User

# Chat Model
class Chat(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name or f'Chat {self.id}'
    
    class Meta:
        db_table = '"barelyaschema"."chat"'

# ChatMember Model
class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} in {self.chat.name}'
    
    class Meta:
        db_table = '"barelyaschema"."chat_member"'


# Message Model
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.username} in {self.chat.name}'
    
    class Meta:
        db_table = '"barelyaschema"."message"'
