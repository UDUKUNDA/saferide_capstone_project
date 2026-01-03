from django.contrib import admin
from .models import User, Chat, Message, Order

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'city', 'roleKey', 'created_at')
    search_fields = ('email', 'username', 'city')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'members', 'created_at')
    list_filter = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'created_at')
    list_filter = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'senderName', 'receiverName', 'origin', 'destination', 'isComplete')
    list_filter = ('isComplete', 'created_at')