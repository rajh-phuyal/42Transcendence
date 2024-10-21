from django.db import models

# Conversation Model
class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    is_group_conversation = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=False)

    def __str__(self):
        return self.name or f'Chat {self.id}'
    
    class Meta:
        db_table = '"barelyaschema"."conversation"'

# ConversationMember Model
class ConversationMember(models.Model):
    # The ForeignKey of django adds a _id suffix to the field name so chat becomes chat_id
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f'{self.user_id.username} in {self.chat_id.name}'
    
    class Meta:
        db_table = '"barelyaschema"."chat_member"'
        unique_together = ('conversation', 'user')

# Message Model
class Message(models.Model):
    id = models.AutoField(primary_key=True)
    # The ForeignKey of django adds a _id suffix to the field name so chat becomes chat_id
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Message from {self.sender.username} in {self.chat.name}'
    
    class Meta:
        db_table = '"barelyaschema"."message"'
