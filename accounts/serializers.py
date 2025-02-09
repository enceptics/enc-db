from rest_framework import serializers
from .models import Profile, User
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.hashers import check_password

from rest_framework import serializers
from django.contrib.auth import get_user_model

class CustomRegisterSerializer(serializers.ModelSerializer):
    
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    role = serializers.ChoiceField(choices=get_user_model().ROLE_CHOICES, required=True)
    email = serializers.EmailField(required=True)
    image = serializers.ImageField(required=False)  # Optional image field
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})  # Password field

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'role', 'email', 'image', 'password']  # Include password

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def save(self):
        user = super().save()  # Don't use commit=False here
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.role = self.validated_data['role']
        user.email = self.validated_data['email']
        user.image = self.validated_data.get('image', None)
        
        # Set the password and hash it
        password = self.validated_data['password']
        user.set_password(password)  # Hash the password

        # Check if the role is 'superuser' and update fields accordingly
        if user.role == user.SUPERUSER:
            user.is_superuser = True
            user.is_staff = True

        user.save()  # Now save the user to the database
        return user

        
class CustomLoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is not registered.")
        return value

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        User = get_user_model()
        user = User.objects.get(email=email)

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password.")

        data['user'] = user
        return data



class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for custom user model updates.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'role', 'image']
        read_only_fields = ['id', 'is_active', 'date_joined']  # Ensure immutable fields are read-only

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model with nested User representation.
    """
    user=CustomUserSerializer()  # Nested serializer for the related user

    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        """
        Customize the representation of the Profile instance.
        """
        data = super().to_representation(instance)
        if not data['profile_pic']:
            data['profile_pic'] = '/media/default.png'  # Use the path to your default image
        return data

    def validate_bio(self, value):
        """
        Custom validation for the "bio" field.
        """
        if len(value) > 500:
            raise serializers.ValidationError("Bio is too long.")
        return value

    def validate_current_city(self, value):
        """
        Custom validation for the "current_city" field.
        """
        if len(value) > 50:
            raise serializers.ValidationError("Current city is too long.")
        return value
