from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('chat/<int:conversation_id>/', views.chat_page, name='chat'),
    path('send-message/<int:conversation_id>', views.send_message, name='send-message'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('chat/<int:conversation_id>/rename/', views.rename_chat, name='rename_chat'),
    path('chat/<int:conversation_id>/delete/', views.delete_chat, name='delete_chat'),

]
