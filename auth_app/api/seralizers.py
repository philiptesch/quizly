from rest_framework import serializers
from auth_app.models import User
from django.contrib.auth import authenticate



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
