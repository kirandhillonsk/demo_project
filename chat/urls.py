

from . import views
from .views import *
from django.conf.urls import url
from django.contrib import admin
from django.urls import path


admin.autodiscover()

app_name = 'chat'

urlpatterns = [
    path('rvt-chat', RVTChat, name='rvt_chat'),
    url(r'^user-chat/$',UserChatScreen, name='user_chat'),
    url(r'^get-updated-users-list/$',GetUpdatedUsersList, name='get_updated_users_list'),
    url(r'^search-chat-user/(?P<id>[-\w]+)/$',SearchChatUser, name='search_chat_user'),
    path("api/un-read-message/", UnreadMessageAPI.as_view(), name="un_read_message"),



    #Api's
]
