from django.urls import path
from . import views
urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:conv_id>/', views.chat_room, name='chat_room'),
    path('<int:conv_id>/send/', views.send_message, name='send_message'),
    path('<int:conv_id>/messages/', views.get_messages, name='get_messages'),
]
