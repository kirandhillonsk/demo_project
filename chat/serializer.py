from email.mime import image
from tokenize import group
from api.models import *
from .models import *
from api.serializer import *
from urllib import request
from django.core import serializers
from rest_framework import response
from rest_framework import serializers
from rest_framework.response import Response



"""
user serializer
"""
class UserChatSerializer(Serializers.ModelSerializer):
    profile_pic = Serializers.ImageField(read_only = True)
    class Meta:
        model = User
        fields = ('id','first_name','last_name','email','profile_pic')



"""
message serializer
"""
class MessageSerializer(serializers.ModelSerializer):
    created_on = serializers.SerializerMethodField()
    sender = UserChatSerializer(read_only = True)
    receiver = UserChatSerializer(read_only = True)
    imagess = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id','imagess','videos','sender','receiver','chat_id','message','created_on','type')

    def get_created_on(self,obj):
        return obj.created_on

    def get_imagess(self,obj):
        img = []
        images = Message.images.through.objects.filter(message_id = obj.id).values_list('chatimage_id',flat=True)
        image = ChatImage.objects.filter(id__in = images)
        for imgs in image:
            img.append({"image":imgs.images.url})
        
        return img

    def get_videos(self,obj):
        vid = []
        videos = Message.video.through.objects.filter(message_id = obj.id).values_list('chatvideo_id',flat=True)
        video = ChatVideo.objects.filter(id__in = videos)
        for vids in video:
            vid.append({"image":vids.video.url,"name":vids.name.url})
        
        return vid


"""
chating serializer
"""
class ChatingSerializer(serializers.ModelSerializer):
    sender = UserChatSerializer(read_only = False)
    receiver = UserChatSerializer(read_only = False)
    created_on = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()


    class Meta:
        model = Chating
        fields = ('id','sender','receiver','created_on','last_message')

    def get_created_on(self,obj):
        return obj.created_on.strftime('%Y-%m-%d %H:%M:%S')

    def get_last_message(self,obj):
        user = self.context['request'].user
        try:
            messages = Message.objects.filter(chat_id = obj.id).order_by("-id")[0]
            messages_count = Message.objects.filter(chat_id = obj.id,seen=0,receiver = user).order_by("-id").count()
            data ={
                "message":messages.message,
                "time":messages.created_on.strftime('%Y-%m-%d %H:%M:%S'),
                "type":messages.type,
                "cout": messages_count
            }
            return data
        except:
            return ''


