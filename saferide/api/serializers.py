from rest_framework import serializers
from .models import User, Chat, Message, Order
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'city', 'roleKey', 'phone', 'latitude', 'longitude', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'roleKey', 'city', 'phone']
    
    def validate_email(self, value):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Please provide a valid email")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with the given email already exists")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'],
            roleKey=validated_data['roleKey'],
            city=validated_data['city'],
            phone=validated_data.get('phone', '')
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password')
        
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password')
        
        refresh = RefreshToken.for_user(user)
        data['user'] = user
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'members', 'created_at', 'updated_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'sender', 'receiver', 'senderName', 'receiverName', 
                  'origin', 'destination', 'isComplete', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']