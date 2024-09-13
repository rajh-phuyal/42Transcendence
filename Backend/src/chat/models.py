from django.db import models

# Chat Model
class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name or f'Chat {self.id}'
    
    class Meta:
        db_table = '"barelyaschema"."chat"'

# ChatMember Model
class ChatMember(models.Model):
    id = models.AutoField(primary_key=True)
    # The ForeignKey of django adds a _id suffix to the field name so chat becomes chat_id
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user_id.username} in {self.chat_id.name}'
    
    class Meta:
        db_table = '"barelyaschema"."chat_member"'


# Message Model
class Message(models.Model):
    id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('user.User', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.username} in {self.chat.name}'
    
    class Meta:
        db_table = '"barelyaschema"."message"'
