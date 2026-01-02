from django.urls import path
from .views import (
    RegisterUserView, LoginUserView, GetCurrentUserView, GetUsersView,
    GetUserByIdView, UpdateUserLocationView, UpdateUserView, UpdatePasswordView,
    DeleteUserView, CreateChatView, UserChatsView, GetAllChatsView, FindChatView,
    AddMessageView, GetMessagesView, CreateOrderView, GetAllOrdersView,
    DeleteOrderView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # User URLs
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('current-user/', GetCurrentUserView.as_view(), name='current-user'),
    path('users/', GetUsersView.as_view(), name='get-users'),
    path('users/<uuid:user_id>/', GetUserByIdView.as_view(), name='get-user'),
    path('users/<uuid:user_id>/location/', UpdateUserLocationView.as_view(), name='update-location'),
    path('users/<uuid:user_id>/update/', UpdateUserView.as_view(), name='update-user'),
    path('users/<uuid:user_id>/password/', UpdatePasswordView.as_view(), name='update-password'),
    path('users/<uuid:user_id>/', DeleteUserView.as_view(), name='delete-user'),
    
    # Chat URLs
    path('chats/', CreateChatView.as_view(), name='create-chat'),
    path('chats/user/<uuid:user_id>/', UserChatsView.as_view(), name='user-chats'),
    path('chats/all/', GetAllChatsView.as_view(), name='all-chats'),
    path('chats/find/<uuid:first_id>/<uuid:second_id>/', FindChatView.as_view(), name='find-chat'),
    
    # Message URLs
    path('messages/', AddMessageView.as_view(), name='add-message'),
    path('messages/<uuid:chat_id>/', GetMessagesView.as_view(), name='get-messages'),
    
    # Order URLs
    path('orders/', CreateOrderView.as_view(), name='create-order'),
    path('orders/all/', GetAllOrdersView.as_view(), name='all-orders'),
    path('orders/<uuid:id>/', DeleteOrderView.as_view(), name='delete-order'),
]