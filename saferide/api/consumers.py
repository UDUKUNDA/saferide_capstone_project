import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import User

class ChatConsumer(AsyncWebsocketConsumer):
    # Track online users globally (in memory for now, use Redis for production scaling)
    # Dictionary format: { user_id: { id, username, roleKey, latitude, longitude, ... } }
    online_users = {}

    @database_sync_to_async
    def get_user_details(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return {
                'id': str(user.id),
                'username': user.username,
                'roleKey': user.roleKey,
                'email': user.email,
                'latitude': user.latitude,
                'longitude': user.longitude
            }
        except User.DoesNotExist:
            return None

    async def connect(self):
        # We can get user from scope if we use auth middleware, or pass via query param/message
        # For now, we'll accept the connection and wait for an "addNewUser" message to identify
        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from online tracking if we know who they are
        if hasattr(self, 'user_id'):
            # Leave their personal group
            await self.channel_layer.group_discard(
                f"user_{self.user_id}",
                self.channel_name
            )
            # Leave global group
            await self.channel_layer.group_discard(
                "global_updates",
                self.channel_name
            )
            # Remove from online set
            if self.user_id in ChatConsumer.online_users:
                ChatConsumer.online_users.pop(self.user_id, None)
                # Broadcast updated list
                await self.broadcast_online_users()
                print(f"User {self.user_id} removed from online list. Total: {len(ChatConsumer.online_users)}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type') or data.get('action') # handle both for flexibility

        if msg_type == 'addNewUser':
            self.user_id = str(data.get('userId'))
            if self.user_id:
                # Add to personal group for direct messaging
                await self.channel_layer.group_add(
                    f"user_{self.user_id}",
                    self.channel_name
                )
                # Add to global group for online status
                await self.channel_layer.group_add(
                    "global_updates",
                    self.channel_name
                )
                
                # Fetch user details and add to online list
                user_details = await self.get_user_details(self.user_id)
                if user_details:
                    ChatConsumer.online_users[self.user_id] = user_details
                    # Broadcast online users to everyone
                    await self.broadcast_online_users()
                    print(f"User {self.user_id} added to online list. Total: {len(ChatConsumer.online_users)}")

        elif msg_type == 'sendMessage':
            # Handle sending a message
            # Expected data: { senderId, recipientId, text }
            recipient_id = data.get('recipientId')
            if recipient_id:
                # Send to recipient's group
                await self.channel_layer.group_send(
                    f"user_{recipient_id}",
                    {
                        'type': 'chat_message',
                        'message': data
                    }
                )
                # Also send back to sender for confirmation/display (optional if frontend handles it)
                # But Socket.IO implementation didn't echo back to sender via socket, usually

        elif msg_type == 'sendOrder':
            # Expected data: { receiverId, ...orderData }
            receiver_id = data.get('receiverId')
            if receiver_id:
                await self.channel_layer.group_send(
                    f"user_{receiver_id}",
                    {
                        'type': 'order_notification',
                        'order': data
                    }
                )

    async def broadcast_online_users(self):
        # Send to "global_updates" group
        await self.channel_layer.group_send(
            "global_updates",
            {
                'type': 'online_users_update',
                'users': list(ChatConsumer.online_users.values())
            }
        ) 

    async def online_users_update(self, event):
        users = event['users']
        await self.send(text_data=json.dumps({
            'type': 'getOnlineUsers',
            'data': users
        }))

    # --- Handlers for group messages ---

    async def chat_message(self, event):
        # Send message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'getMessage', # Match Socket.IO event name for frontend compatibility
            'data': message
        }))
        
        # Also send notification
        await self.send(text_data=json.dumps({
            'type': 'getNotification',
            'data': {
                'senderId': message['senderId'],
                'message': message['text'],
                'isRead': False,
                'date': str(datetime.now()) # simplistic date
            }
        }))

    async def order_notification(self, event):
        order = event['order']
        await self.send(text_data=json.dumps({
            'type': 'getOrder',
            'data': order
        }))

from datetime import datetime
