from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ephemeral_messages_service, name='ephemeral_messages_service'),
    url(r'^chat/$', views.create_message, name='create_message'),
    url(r'^chat/(?P<chat_id>\d+)$', views.get_message, name='get_message'),
    url(r'^chats/(?P<user_name>\w+)$', views.get_user_messages, name='get_user_messages'),
]