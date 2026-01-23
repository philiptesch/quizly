from rest_framework import serializers
from auth_app.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

class RegistrationSerializer(serializers.ModelSerializer):


    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirmed_password', 'email']


    def validate(self, data):
            if data['password'] != data['confirmed_password']:
                raise serializers.ValidationError({'password': 'Passwords do not match'})
            return data
    

    def create(self, validated_data):
         
        password = validated_data['password']

        account = User(email=validated_data['email'], username=validated_data['username'])
        account.set_password(password)
        account.save()
        return account

class LoginSeralizer(TokenObtainPairSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'password', 'email']
        extra_kwargs = {
            'username': {'write_only': True},
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        
        username = attrs.get("username")
        password = attrs.get("password")
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("username not exist")
        
        if not user.check_password(password):
            raise serializers.ValidationError("wrong password")
        
        data = super().validate({"username": user.username, "password": password})
        return data
