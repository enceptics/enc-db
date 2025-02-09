from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from allauth.account.views import SignupView
from allauth.account.utils import perform_login
from django.contrib.auth import get_user_model
from dj_rest_auth.views import UserDetailsView
from .serializers import CustomUserSerializer, CustomRegisterSerializer, CustomLoginSerializer
from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from accounts.forms import CustomSignupForm
from rest_framework.serializers import ModelSerializer
from .models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from dj_rest_auth.registration.views import RegisterView

# Google login function
@csrf_exempt
def google_login(request):
    if request.method == 'POST':
        try:
            # Parse the JSON request body
            data = json.loads(request.body)
            token = data.get('token')  # Get the token from the request body
            if not token:
                return JsonResponse({"detail": "Token is missing"}, status=400)

            # Verify the token with Google's API
            idinfo = id_token.verify_oauth2_token(token, Request(), settings.GOOGLE_CLIENT_ID)

            # Check if the user exists or create a new one
            email = idinfo['email']
            user, created = User.objects.get_or_create(email=email)

            if created:
                # If the user is new, populate additional fields
                user.first_name = idinfo.get('given_name', '')
                user.last_name = idinfo.get('family_name', '')
                user.save()

            # Generate or retrieve a token for the user
            auth_token, created = Token.objects.get_or_create(user=user)

            # Respond with the token and user information
            return JsonResponse({
                "success": True,
                "token": auth_token.key,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=200)

        except ValueError:
            return JsonResponse({"detail": "Invalid token"}, status=400)
    else:
        return JsonResponse({"detail": "Invalid request method"}, status=405)

class CustomRegisterView(APIView):
    serializer_class = CustomRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = CustomRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            # If serializer is valid, save the user
            user = serializer.save()
            return Response(
                {"success": True, "user_id": user.id, "email": user.email},
                status=status.HTTP_201_CREATED
            )
        else:
            # If validation fails, return the error messages
            return Response(
                serializer.errors,  # Send back the validation errors
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomLoginView(APIView):
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = CustomLoginSerializer(data=request.data)

        # Validate the serializer and check for authentication
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate or retrieve an auth token
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {"token": token.key, "user_id": user.id, "email": user.email},
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = CustomUserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"detail": f"Validation error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomUserDetailsView(UserDetailsView):
    serializer_class = CustomUserSerializer

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Profile ViewSet
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('-created_at')
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = self.get_serializer(profile, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            return Response({"detail": f"Integrity error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"detail": f"Validation error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_valid(self, form):
        response = super().form_valid(form)
        perform_login(self.request, self.user, email_verification='optional')
        return response
