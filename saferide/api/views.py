from django.shortcuts import render

 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User, Chat, Message, Order
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    ChatSerializer, MessageSerializer, OrderSerializer
)
import os
from google.cloud import translate_v2 as translate
from django.conf import settings

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

