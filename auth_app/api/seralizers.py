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
        """
        Validate that both entered passwords match during registration.

        Validation Steps:
        1. Retrieve the password and confirmed_password from the input data.
        2. Compare both password fields.
        3. Raise a validation error if the passwords do not match.
        4. Return the validated data if the passwords are identical.
        """

        if data['password'] != data['confirmed_password']:
                raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data
    

    def create(self, validated_data):
        """
        Create a new user account with a securely hashed password.

        Creation Steps:
        1. Extract the password from the validated data.
        2. Create a new User instance with the provided username and email.
        3. Hash the password using Django's set_password method.
        4. Save the user account to the database.
        5. Return the created user instance.
        """

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
        extra_kwargs = {'username': {'write_only': True},'password': {'write_only': True},}

    def validate(self, attrs):
        """
        Validate user login credentials and generate JWT tokens.

        Validation Steps:
        1. Retrieve the username and password from the request data.
        2. Check if a user with the given username exists.
        3. Raise a validation error if the user does not exist.
        4. Verify the provided password against the stored hashed password.
        5. Raise a validation error if the password is incorrect.
        6. Call the parent TokenObtainPairSerializer validation to generate access and refresh tokens.
        7. Return the token data.
        """
        
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
