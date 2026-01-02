from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User, Chat, Message, Order
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    ChatSerializer, MessageSerializer, OrderSerializer
)
from google.cloud import translate_v2 as translate
import json

class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate token
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'city': user.city,
                'roleKey': user.roleKey,
                'phone': user.phone,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                'data': {
                    'token': serializer.validated_data['access'],
                    'user': {
                        'id': str(user.id),
                        'username': user.username,
                        'email': user.email,
                        'city': user.city,
                        'roleKey': user.roleKey,
                        'phone': user.phone
                    }
                },
                'message': 'Login successful'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetCurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'data': serializer.data})

class GetUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

class GetUserByIdView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'id'

class UpdateUserLocationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if latitude is None or longitude is None:
            return Response(
                {'message': 'Latitude and longitude are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.latitude = latitude
        user.longitude = longitude
        user.save()
        
        return Response({
            'message': 'User location updated successfully',
            'user': UserSerializer(user).data
        })

class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'User details updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        new_password = request.data.get('newPassword')
        
        if not new_password:
            return Response(
                {'message': 'New password is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'User password updated successfully'})

class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'id'
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'User deleted successfully'})

class CreateChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        sender_id = request.data.get('senderId')
        receiver_id = request.data.get('receiverId')
        
        if not sender_id or not receiver_id:
            return Response(
                {'error': 'senderId and receiverId are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if chat already exists
        existing_chat = Chat.objects.filter(
            members__contains=[sender_id, receiver_id]
        ).first()
        
        if existing_chat:
            return Response(ChatSerializer(existing_chat).data)
        
        chat = Chat.objects.create(members=[sender_id, receiver_id])
        return Response(ChatSerializer(chat).data, status=status.HTTP_201_CREATED)

class UserChatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        chats = Chat.objects.filter(members__contains=[user_id])
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)

class GetAllChatsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

class FindChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, first_id, second_id):
        # Find chat where members contain both users
        chat = Chat.objects.filter(
            members__contains=[first_id, second_id]
        ).first()
        
        if chat:
            return Response(ChatSerializer(chat).data)
        return Response(
            {'message': 'Chat not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
import json

class AddMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        chat_id = request.data.get('chatId')
        sender_id = request.data.get('senderId')
        text = request.data.get('text')
        sender_language = request.data.get('senderLanguage', 'en')
        
        if not all([chat_id, sender_id, text]):
            return Response(
                {'error': 'chatId, senderId, and text are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chat = Chat.objects.get(id=chat_id)
            sender = User.objects.get(id=sender_id)
            
            # Google Cloud Translation
            try:
                # Initialize translation client
                # Note: You need to set GOOGLE_APPLICATION_CREDENTIALS environment variable
                translate_client = translate.Client()
                
                # Translate text
                if sender_language != 'en':
                    result = translate_client.translate(
                        text, 
                        target_language=sender_language
                    )
                    translated_text = result['translatedText']
                else:
                    translated_text = text
            except Exception as e:
                print(f"Translation error: {e}")
                translated_text = text  # Fallback to original text
            
            message = Message.objects.create(
                chat=chat,
                sender=sender,
                text=translated_text
            )
            
            return Response(MessageSerializer(message).data)
            
        except Chat.DoesNotExist:
            return Response(
                {'error': 'Chat not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetMessagesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id):
        try:
            messages = Message.objects.filter(chat_id=chat_id).order_by('created_at')
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

class DeleteOrderView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    lookup_field = 'id'
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Order deleted successfully'})