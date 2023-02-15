
import datetime
import environ
import timeago
from .models import *
from api.serializer import *
from accounts.models import *
from accounts.constants import *
from django.http import JsonResponse
from rest_framework_jwt.views import *
from rest_framework.views import APIView
from django.db.models.query_utils import Q
from rest_framework.response import Response
from django.shortcuts import redirect, render
from rest_framework import status,permissions
from django.views.decorators.csrf import csrf_exempt
from rest_framework import response,status,permissions
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets,response,status,permissions
from .serializer import *
from rvt_lvt.models import *

env = environ.Env()
environ.Env.read_env()


"""
user list
"""
def RVTChat(request):
    BANK_ADD_URL = env('BANK_ADD_URL')

    connectId = []        
    frndidArray = {} 
    last_chatings = Chating.objects.filter(
        Q(sender = request.user)|
        Q(receiver_id = request.user)
    )

    for i in last_chatings:        
        if request.user.id != i.sender_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.sender_id
            frndidArray[i.id] = i.receiver_id

        if request.user.id != i.receiver_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.receiver_id
    x = []
    my_list = sorted(set(frndidArray))
    for frndid in my_list:

        last_message = Message.objects.filter(chat_id = frndid).order_by('-id')[:1]
        for i in last_message:
            x.append(i.id)

    last_message = Message.objects.filter(id__in = x)    
    return render(request , "rvt/rvt-chat.html" , {"title":"Inbox", "nbar" : "rvt_chat","last_message":last_message,'BANK_ADD_URL':BANK_ADD_URL })



"""
Unread message 
"""
class UnreadMessageAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request,*args,**kwargs):
        un_read = Message.objects.filter(receiver=request.user, seen = False).values_list('chat',flat=True)
        chat = Chating.objects.filter(id__in = un_read)
        serializer = ChatingSerializer(chat, many = True, context={'request': request})
        return Response({"data":serializer.data,"url":request.path})


"""
Send message api
"""
class ChatingViewset(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChatingSerializer
    
    def get_queryset(self):
        if self.request.data.get("receiver_user") is None:
            return Chating.objects.filter(Q(sender = self.request.user.id)|Q(receiver = self.request.user.id ))
        else:
            chatings = Chating.objects.filter(
                Q(sender = self.request.user.id,receiver_id = self.request.query_params.get("receiver_user"))|
                Q(sender =self.request.query_params.get("receiver_user"),receiver_id =  self.request.user.id)
            )
            if not chatings:
                response.Response({"message":"Invialid chating."},status = status.HTTP_400_BAD_REQUEST)
           
            return chatings 

    def create(self,request,*args,**kwargs):
        images =[]
        videos = []
        user = User.objects.get(id=request.user.id)
        id = request.data.get("receiver_user",None) 
        receiver_user = User.objects.get(id=id)
        if not id:
            return Response({"error":"Please set receiver user to start chat"},status = 400)
    
        try:
            chating = Chating.objects.get(Q(sender = user,receiver_id = id)|Q(sender_id = id,receiver = user))

        except Chating.DoesNotExist:
            chating = Chating.objects.create(sender = user,receiver_id = id)   


        for i in range(0,int(request.data.get("image_count",'0'))+1):
            if request.FILES.get("image{}".format(i),None):
                images.append(ChatImage.objects.create(images = request.FILES.get("image{}".format(i))))

        for i in range(0,int(request.data.get("video_count",'0'))+1):
            if request.FILES.get("video{}".format(i),None) and request.FILES.get("name{}".format(i),None):
                videos.append(
                    ChatVideo.objects.create(
                        video = request.FILES.get("video{}".format(i)),
                        name=request.FILES.get("name{}".format(i),None)
                        )
                )
        message = Message.objects.create(sender = user,
            receiver = receiver_user,
            chat = chating,
            message = request.data.get("message"),
            type = request.data.get("type"),
            sender_seen = True)

        if images:
            for image in images:
                message.images.add(image.id)
        
        if videos:
            for vid in videos:
                message.video.add(vid.id)
        data= MessageSerializer(message,context = {"request":request}).data
        return Response({"data":data,"message":"Message send Successfully.","status":status.HTTP_200_OK,"url":request.path},status=200)





class MessageWindowAPIView(APIView):
    def get(self, request, *args, **kwargs):

        if not request.query_params.get("receiver_user",None):
            response.Response({"message":"Please select a receiver user to start chat."},status=status.HTTP_400_BAD_REQUEST)

        chatings = Chating.objects.filter(
            Q(sender = request.user,receiver_id = request.query_params.get("receiver_user"))|
            Q(sender_id = request.query_params.get("receiver_user"),receiver = request.user)
        ).values_list('id',flat=True)

        if not chatings:
            response.Response({"message":"Invialid chating."},status = status.HTTP_400_BAD_REQUEST)
        messages = Message.objects.filter(Q(chat_id__in = chatings,sender = request.user)|(Q(chat_id__in = chatings,receiver_id = request.user.id,seen=1))).order_by('-id')  
        serializer = MessageSerializer(messages, many = True, context={'request': request})
        return Response({"data": serializer.data,"status": status.HTTP_200_OK},status = status.HTTP_200_OK)


class chat_unread(APIView):
    def get(self,request,*args,**kwargs):

        chatings = Chating.objects.filter(Q(receiver = request.user)|(Q(sender=request.user)))
        messages = Message.objects.filter(chat__in = chatings, receiver=request.user,seen=0)
        messages=MessageSerializer(messages,many = True,context = {"request":self.request}).data

        messagesRead = Message.objects.filter(chat__in = chatings, receiver=request.user,seen=0)
        messagesRead.update(seen = 1)

        return Response({"data": messages,"status": status.HTTP_200_OK},status = status.HTTP_201_CREATED)

"""
load message
"""
class LoadMessageAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return response.Response({"message":"User Does not exist"},status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = User.objects.get(id=request.query_params.get('user_id'))
        except:
            return response.Response({"message":"Other User User Does not exist"},status=status.HTTP_400_BAD_REQUEST)

        if other_user.is_superuser:
            chating = Chating.objects.filter(Q(sender=user)|Q(receiver = user)).values_list('id',flat=True)
        else:
            chating = Chating.objects.filter(Q(sender=user)|Q(receiver = user)).values_list('id',flat=True)
        messages = Message.objects.filter(chat_id__in=chating, receiver=user, seen=False)
        data = MessageSerializer(messages,many=True,context={"request":request}).data
        seen_messages = Message.objects.filter(chat_id__in=chating, receiver=user, seen=False)
        seen_messages.update(seen=True)
        other_user = {
            "id": other_user.id,
            "full_name": other_user.full_name if other_user.full_name else "",
            "email": other_user.email if other_user.email else "",
            "mobile_no": other_user.mobile_no,
            "country_code": other_user.country_code,
            "profile_pic": env('BASE_URL') + other_user.profile_pic.url if other_user.profile_pic else "",
        }
        return Response({"messages":data,"other_user":other_user,"status":status.HTTP_200_OK,'url' : self.request.path}, status=status.HTTP_200_OK)



"""
user chat screen
"""
@login_required
def UserChatScreen(request):

    to = User.objects.get(id = request.GET.get("id"))
    chatings = Chating.objects.filter(
        Q(sender = request.user,receiver_id = request.GET.get("id"))|
        Q(receiver = request.user,sender_id = request.GET.get("id"))
    )
    all_message = Message.objects.filter(chat_id__in =  chatings)
    final_all_message = Message.objects.filter(chat_id__in =  chatings).values_list("id",flat=True)

    message_image = Message.images.through.objects.filter(message_id__in = final_all_message).values_list("chatimage_id",flat=True)
    image = ChatImage.objects.filter(id__in = message_image)
  
    connectId = []        
    frndidArray = {} 
    last_chatings = Chating.objects.filter(
        Q(sender = request.user)|
        Q(receiver_id = request.user)
    )

    for i in last_chatings:        
        if request.user.id != i.sender_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.sender_id
            frndidArray[i.id] = i.receiver_id

        if request.user.id != i.receiver_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.receiver_id
    x = []
    my_list = sorted(set(frndidArray))
    for frndid in my_list:

        last_message = Message.objects.filter(chat_id = frndid).order_by('-id')[:1]
        for i in last_message:
            x.append(i.id)

    last_message = Message.objects.filter(id__in = x).order_by("-id")

    recipient_id = to.id
    sender_id = request.user.id
    
    shared_appointments = Appointments.objects.filter(
        Q(created_by__id = recipient_id,created_for__id = sender_id)|
        Q(created_for__id = recipient_id,created_by__id = sender_id)
    )


    return render(request , 'rvt/rvt-chat-window.html',{"mesaage_to":to.username,"to":to,"all_message":all_message,"last_message":last_message,"nbar":"rvt_chat","image":image, "shared_appointments":shared_appointments})



@login_required
def GetUpdatedUsersList(request):
    
    connectId = []        
    frndidArray = {} 
    last_chatings = Chating.objects.filter(
        Q(sender = request.user)|
        Q(receiver_id = request.user)
    )

    for i in last_chatings:        
        if request.user.id != i.sender_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.sender_id
            frndidArray[i.id] = i.receiver_id

        if request.user.id != i.receiver_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.receiver_id
    x = []
    my_list = sorted(set(frndidArray))
    for frndid in my_list:

        last_message = Message.objects.filter(chat_id = frndid).order_by('-id')[:1]
        for i in last_message:
            x.append(i.id)

    last_message = Message.objects.filter(id__in = x).order_by('-id')
    usersList = []
    for i in last_message:
        if i.receiver == request.user:
            data = {
                "id": i.sender_id,
                "name": i.sender.first_name + ' ' +i.sender.last_name,
                "profile_image": i.sender.profile_pic.url if i.sender.profile_pic else "/static/admin-assets/images/default.png",
                "message": (i.message[:30] + '...' if len(i.message)>30 else i.message) if i.message else "",
                "time": timeago.format(i.created_on.time(), datetime.now()),
                "count":'1'
            }
        else:
            data = {
                "id": i.receiver_id,
                "name": i.receiver.first_name + ' ' +i.receiver.last_name,
                "profile_image": i.receiver.profile_pic.url if i.receiver.profile_pic else "/static/admin-assets/images/default.png",
                "message": (i.message[:30] + '...' if len(i.message)>30 else i.message) if i.message else "",
                "time": timeago.format(i.created_on.time(), datetime.now()),
                "count": "10"
            }


        if data:
            usersList.append(data)

    return JsonResponse(usersList, safe=False)


"""
search 
"""
def SearchChatUser(request,id):
    search = request.GET.get("search")
    searchuser = User.objects.filter(first_name__icontains = request.GET.get("user_id")).values_list("id",flat=True)

    to = User.objects.get(id = id)
    chatings = Chating.objects.filter(
        Q(sender = request.user,receiver_id = id)|
        Q(receiver = request.user,sender_id = id)
    )
    all_message = Message.objects.filter(chat_id__in =  chatings)

    connectId = []        
    frndidArray = {} 
    last_chatings = Chating.objects.filter(
        Q(sender = request.user)|
        Q(receiver_id = request.user)
    )

    for i in last_chatings:        
        if request.user.id != i.sender_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.sender_id
            frndidArray[i.id] = i.receiver_id

        if request.user.id != i.receiver_id:
            connectId.append(i.id)
            frndidArray[i.id] = i.receiver_id
    x = []
    my_list = sorted(set(frndidArray))
    for frndid in my_list:

        last_message = Message.objects.filter(chat_id = frndid).order_by('-id')[:1]
        for i in last_message:
            x.append(i.id)

    last_message = Message.objects.filter(id__in = x)

    return redirect('enduser:users_chat_screen' ,id=id)

