

from urllib import request
from django.db import models
from accounts.models import *



"""
chat image
"""
class ChatImage(models.Model):
    images = models.ImageField(upload_to='chat_image',null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True;
        db_table = 'tbl_chat_image'

"""
chat video
"""
class ChatVideo(models.Model):
    video = models.FileField(upload_to='chat_video',blank=True,null=True)
    name = models.FileField(upload_to='chat_thumb',blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True;
        db_table = 'tbl_chat_video'



class Chating(models.Model):
    sender = models.ForeignKey(User,related_name="chat_sender",on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(User,related_name="chat_receiver",on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        managed = True;
        db_table = 'tbl_chats' 


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver', null=True, blank=True)
    message = models.TextField(null=True,blank=True)
    type = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='chat',blank= True,null = True)
    images = models.ManyToManyField(ChatImage)
    video = models.ManyToManyField(ChatVideo)
    chat = models.ForeignKey(Chating, related_name="messages", on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    seen = models.IntegerField(default=0)
    sender_seen = models.BooleanField(default=False)

    class Meta:
        managed = True;
        db_table = 'tbl_message'
