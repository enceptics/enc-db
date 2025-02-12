from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from authentication.models import  About, Room, CheckIn, Place, PlaceInfo, Booking, Payment, ExtraCharge, Review, HeroSection
from .serializers import (AboutSerializer,
                            CheckinSerializer,
                            PlaceSerializer,
                            PlaceInfoSerializer,
                            BookingSerializer,
                            PaymentSerializer,
                            ReviewSerializer,
                            HeroSectionSerializer,

                         )

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status, filters
from rest_framework.response import Response
from django.db.models import Q  # Import Q for complex lookups
from rest_framework.decorators import action  # Import the action decorator
from .permissions import IsAuthorOrReadOnly
from django.contrib.auth.decorators import login_required
import requests
import paypalrestsdk
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
import os
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
import json
import base64
import paypalrestsdk
import logging  # Import the logging module
from datetime import datetime, timedelta
from authentication.utils import make_paypal_payment,verify_paypal_payment
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.db.models import Q, Sum
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Q
# Create a logger
logger = logging.getLogger(__name__)

class GoogleAuthCallbackView(APIView):
    def get(self, request):
        # Handle the Google authentication callback
        # Extract the token from the request
        token = request.GET.get('token')

        # Verify the token with Google
        response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
        if response.status_code == 200:
            user_info = response.json()
            email = user_info.get('email')

            # Check if the user already exists
            user, created = User.objects.get_or_create(email=email)

            if created:
                user.username = email.split('@')[0]
                user.first_name = user_info.get('given_name', '')
                user.last_name = user_info.get('family_name', '')
                user.image = user_info.get('picture') 
                user.save()

            # Generate or retrieve an auth token
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {"token": token.key, "user_id": user.id, "email": user.email},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetUserRole(APIView):
    def get(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Get the user's role based on your authentication logic
            user_role = "superuser" if request.user.is_superuser else "regular"
            return Response({"role": user_role})
        else:
            return Response({"role": "anonymous"}, status=status.HTTP_401_UNAUTHORIZED)


class HeroSectionView(viewsets.ModelViewSet):
    queryset = HeroSection.objects.all()  # Queryset to get all HeroSection instances
    serializer_class = HeroSectionSerializer  # Serializer to convert HeroSection objects to JSON

# booking
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def calculate_checkout_date(self, checkin_date):
        checkin_datetime = datetime.strptime(checkin_date, '%Y-%m-%d')
        checkout_datetime = checkin_datetime + timedelta(days=1)  # Adjust the number of days as needed
        return checkout_datetime.strftime('%Y-%m-%d')

    def calculate_extra_charges_for_kids(self):
        # Define the price per kid
        price_per_kid = 1000  # Adjust the price as needed
        # Extract the number of kids from the request data
        num_kids = self.request.data.get('numKids', 0)  # Default to 0 if not provided

        # Calculate extra charges for kids
        extra_charges_for_kids = num_kids * price_per_kid
        return extra_charges_for_kids

    def calculate_extra_charges_for_adults(self):
        # Define the price per adult
        price_per_adult = 3000  # Adjust the price as needed
        # Extract the number of adults from the request data
        num_adults = self.request.data.get('numAdults', 1)  # Default to 1 if not provided
        # Subtract 1 for the default adult (you can adjust this logic if needed)
        extra_charges_for_adults = (num_adults - 1) * price_per_adult
        return extra_charges_for_adults

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            if 'checkin_date' in data and 'checkout_date' not in data:
                # Calculate the checkout_date if it's missing
                data['checkout_date'] = self.calculate_checkout_date(data['checkin_date'])

            # Ensure the user is authenticated
            if not self.request.user.is_authenticated:
                return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

                # Assign the user based on the currently logged-in user's ID
            data['user'] = self.request.user.id  # Use the currently logged-in user's ID
            # Extract the selected place ID from the request data

            place_id = data.get('place')
            # Check if the place with the given place_id exists
            try:
                 place = Place.objects.get(id=place_id)
            except Place.DoesNotExist:
                return Response({"error": "Selected place does not exist."}, status=status.HTTP_400_BAD_REQUEST)
                # Assign the selected place to the booking
            data['place'] = place.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Log response data
            logging.debug(f"Response data: {serializer.data}")
            # Now, calculate extra charges and add them to the booking
            booking = serializer.instance  # Get the created booking instance
            # Calculate extra charges for different types (e.g., 'Kids' and 'Adults')
            extra_charges_for_kids = self.calculate_extra_charges_for_kids()
            extra_charges_for_adults = self.calculate_extra_charges_for_adults()
            # Create and save ExtraCharge instances for each type
            ExtraCharge.objects.create(booking=booking, type='Kids', amount=extra_charges_for_kids)
            ExtraCharge.objects.create(booking=booking, type='Adults', amount=extra_charges_for_adults)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            logging.debug(f"Data being sent to the backend: {data}")


        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating booking: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Existing view using the Payment model
class PaymentListView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Modify your create method as needed

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only the author of a place (manager or sub_manager) to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # Allow safe methods (GET, OPTIONS, HEAD)
            return True
        # Only allow the manager or sub_manager to edit or delete
        # Ensure we check for None to prevent errors if manager or sub_manager is not set
        return (obj.manager == request.user or obj.sub_manager == request.user) if obj.manager or obj.sub_manager else False


class PlaceViewset(viewsets.ModelViewSet):
    queryset = Place.objects.all().order_by('-id')
    serializer_class = PlaceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name__icontains', 'price__icontains', 'description__icontains']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrReadOnly]

    @action(detail=False, methods=['GET'])
    def filter_by_category(self, request):
        category = request.query_params.get('category', '')
        if not category:
            return Response({"error": "Category parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        filtered_places = Place.objects.filter(category_type=category).order_by('-created_at')
        serializer = PlaceSerializer(filtered_places, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def search(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        results = Place.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('-created_at')

        serializer = PlaceSerializer(results, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Ensure only users with the roles 'PropertyManager' or 'Manager' can create a place.
        Assign the logged-in user to the manager field.
        """
        user = self.request.user
        if user.role not in ['property_manager', 'manager']:
            raise PermissionDenied("You do not have permission to add a place.")
        # Assign the current user as the manager
        serializer.save(manager=user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)  # Ensure the user has the right role
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating place: {str(e)}")  # Log the error
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating place: {str(e)}")  # Log the error
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting place: {str(e)}")  # Log the error
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Optional: Handle exceptions globally
    def handle_exception(self, exc):
        # You can modify this function to handle errors in a more granular or global way
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManagerPlaceViewset(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for managers to see only the places they manage.
    """
    serializer_class = PlaceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only the places managed by the logged-in manager.
        """
        user = self.request.user

        # Ensure only users with a manager role access this endpoint
        if user.role not in ['property_manager', 'manager']:
            return Place.objects.none()  # Return empty queryset if not a manager

        return Place.objects.filter(Q(manager=user) | Q(sub_manager=user)).order_by('-id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        places = []

        for place in queryset:
            # Retrieve statistics directly from the Place model
            places.append({
                "id": place.id,
                "name": place.name,
                "bookings": place.total_bookings,
                "earnings": place.total_earnings,
                "visitors": place.total_visitors,
                "pendingBookings": place.total_pending_bookings,
                "completedBookings": place.total_completed_bookings,
                "canceledBookings": place.total_canceled_bookings,
                "bookingTrend": place.booking_trend,  # Directly use the stored trend
                "forecast": place.revenue_forecast,  # Directly use the stored forecast
                "image": place.cover_image.url if place.cover_image else '',
                "location": place.location,
            })

        return Response(places)

    def calculate_booking_trend(self, place):
        # Implement logic to calculate booking trends for the place
        # For example, you might want to aggregate bookings over time
        return [5, 7, 8, 6, 10, 12, 15]  # Placeholder for actual trend data

    def calculate_forecast(self, place):
        # Implement logic to calculate the revenue forecast for the place
        return [2000, 2500, 3000, 3200, 3500, 3700, 4000]  # Placeholder for actual forecast data

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticated]

    # Retrieve all reviews for a specific place
    @action(detail=True, methods=['GET'])
    def get_reviews(self, request, pk=None):
        try:
            place = Place.objects.get(pk=pk)
            reviews = Review.objects.filter(place=place).order_by('-created_at')
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        except Place.DoesNotExist:
            return Response({"error": "Place not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Post a review for a specific place
    @action(detail=True, methods=['POST'])
    def add_review(self, request, pk=None):
        try:
            place = Place.objects.get(pk=pk)
            user = request.user

            data = request.data
            data['user'] = user.id  # Attach the authenticated user
            data['place'] = place.id  # Attach the place being reviewed

            serializer = ReviewSerializer(data=data)
            if serializer.is_valid():
                serializer.save()

                # Update place's rating and review count after adding the review
                place.total_reviews += 1
                place.average_rating = place.reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
                place.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Place.DoesNotExist:
            return Response({"error": "Place not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlaceInfoViewset(viewsets.ModelViewSet):
    queryset = PlaceInfo.objects.all().order_by('-id')
    serializer_class = PlaceInfoSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

class CheckoutView(APIView):
    def post(self, request):
        room = get_object_or_404(Room, pk=request.data['pk'])
        checked_in_room = CheckIn.objects.get(room__pk=request.data['pk'])
        print(checked_in_room)
        room.is_booked = False
        room.save()

        return Response({"Checkout Successful"}, status=status.HTTP_200_OK)

class CheckedInView(generics.ListAPIView):
    # permission_classes = (IsAdminUser, )
    serializer_class = CheckinSerializer
    queryset = CheckIn.objects.order_by('-id')

def email_confirm_redirect(request, key):
    return HttpResponseRedirect(
        f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/"
    )
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from dj_rest_auth.views import PasswordResetView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

class CustomPasswordResetView(PasswordResetView):
    def send_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        domain = "enceptics.com"

        # Construct the URL with your custom base URL
        url = f"https://{domain}/password-reset/confirm/?uidb64={uid}&token={token}"
        
        subject = "Password Reset Requested"
        email_template_name = "password_reset_email.txt"  # Adjust path as needed
        context = {
            "email": user.email,
            "url": url,
            "domain": settings.EMAIL_CONFIRM_REDIRECT_BASE_URL,
        }
        email = render_to_string(email_template_name, context)
        send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email])


from dj_rest_auth.views import PasswordResetConfirmView
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

# class CustomPasswordResetConfirmView(PasswordResetConfirmView):
#     def post(self, request, *args, **kwargs):
#         # Call the parent method to handle the password reset
#         super().post(request, *args, **kwargs)

#         # If the password reset was successful, you can return a custom response
#         return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

# def password_reset_confirm_redirect(request, uidb64, token):
#     try:
#         # Decode the uidb64 to get the user ID
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User.objects.get(pk=uid)

#         # Check if the token is valid
#         if default_token_generator.check_token(user, token):
#             # If valid, redirect to the confirmation page
#             return HttpResponseRedirect(
#                 f"https://enceptics.com/password-reset/confirm/?uidb64={uidb64}&token={token}"
#             )
#         else:
#             # Token is invalid, redirect to an error page or return an error response
#             return HttpResponseRedirect("https://enceptics.com/password-reset/error/")
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         # User not found or decoding error, redirect to an error page
#         return HttpResponseRedirect("https://enceptics.com/password-reset/error/")

# def create_password_reset_token(user):
#     return default_token_generator.make_token(user)

# def generate_password_reset_link(user):
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))  # Remove .decode()
#     token = create_password_reset_token(user)

#     # Ensure the correct URL pattern is used
#     reset_link = f"https://enceptics.com/api/auth/password-reset/confirm/{uidb64}/{token}/"
#     return reset_link

#     # Ensure the base URL is correct
#     reset_link = f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
#     return reset_link

# from django.core.mail import send_mail

# def send_password_reset_email(user):
#     reset_link = generate_password_reset_link(user)
#     subject = "Hello from enceptics.com"
#     message = f"Please click the link below to reset your password:\n{reset_link}"
    
#     # Using the default from settings for the sender email
#     send_mail(
#         subject,
#         message,
#         settings.DEFAULT_FROM_EMAIL,  # Default sender email from settings
#         [user.email],
#         fail_silently=False,
#     )

# Updating PasswordResetRequestView to use strip_tags
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes, force_str

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uid}/{token}/"
        
        # Send email
        subject = "Password Reset Request - Enceptics"
        message = f"Hello from enceptics.com,\n\nPlease use the following link to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email."
        
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        
        return Response({'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({'error': 'Invalid token or user ID.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)

def booking_success(request):
    # Perform any necessary actions for a successful booking
    # For example, display a success message and render a template
        return Response({'message': 'Booking successfully'})
def booking_failure(request):
    # Perform any necessary actions for a failed booking
    # For example, display a failure message and render a template
        return Response({'message': 'Booking failed'})

# Paypal payment

def paypalToken(client_ID, client_Secret):

    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {
                "client_id":client_ID,
                "client_secret":client_Secret,
                "grant_type":"client_credentials"
            }
    headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Basic {0}".format(base64.b64encode((client_ID + ":" + client_Secret).encode()).decode())
            }

    token = requests.post(url, data, headers=headers)
    return token.json()['access_token']

clientID = getattr(settings, 'PAYPAL_SANDBOX_CLIENT_ID')
clientSecret = getattr(settings, 'PAYPAL_SANDBOX_CLIENT_SECRET')


class PaypalPaymentView(APIView):
    """
    Endpoint for creating a PayPal payment URL.
    """
    def post(self, request, *args, **kwargs):
        print("PaypalPaymentView is executed")
        print(request.data)
        # Fetch the relevant data from the request
        place_id = request.data.get("id")

        # Retrieve the associated Place object
        place = get_object_or_404(Place, id=place_id)

        # Extract the price from the Place object
        price = place.price

        formatted_price = "{:.2f}".format(price)
        print("Price from Place object:", price)

        # Perform PayPal payment request
        status, payment_id, approved_url = make_paypal_payment(
            formatted_price,
            currency="USD",
            return_url="https://enceptics.vercel.app//payment/status/success",
            cancel_url="https://enceptics.vercel.app//payment/status/cancel/"
        )

        print("PayPal API Response:")
        print(json.dumps({"status": status, "payment_id": payment_id, "approved_url": approved_url}, indent=2))

        if status:
            # Save payment information and set is_complete based on payment status
            payment, created = Payment.objects.get_or_create(payment_id=payment_id)
            payment.is_complete = True if payment.status == "approved" else False
            payment.save()

            # Return a response indicating success and the approved URL
            return Response({"success": True, "msg": "Payment link has been successfully created", "approved_url": approved_url}, status=201)
        else:
            return Response({"success": False, "msg": "Authentication or payment failed"}, status=400)

class PaypalValidatePaymentView(APIView):
    """
    endpoint for validate payment
    """
    permission_classes=[permissions.IsAuthenticated,]
    def post(self, request, *args, **kwargs):
        payment_id=request.data.get("payment_id")
        payment_status=verify_paypal_payment(payment_id=payment_id)
        if payment_status:

            return Response({"success":True,"msg":"payment approved"},status=200)
        else:
            return Response({"success":False,"msg":"payment failed or cancelled"},status=200)

# Pesapal

from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
import requests
import json
import random
from accounts.models import User  

# Use environment-based base URL
PESAPAL_ENV = settings.PESAPAL_ENV  # Define this in your Django settings
BASE_URLS = {
    "sandbox": "https://cybqa.pesapal.com/pesapalv3",
    "live": "https://pay.pesapal.com/v3"
}
BASE_URL = BASE_URLS.get(PESAPAL_ENV, BASE_URLS["live"])


def get_access_token():
    """Fetch Pesapal access token dynamically"""
    url = f"{BASE_URL}/api/Auth/RequestToken"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {
        "consumer_key": 'oVgQEkbYBl919gApAiExg/XZrngD4saN',
        "consumer_secret": 'so6meZv/gAO2hRbKalx1w44tTWI='
    }
    response = requests.post(url, json=data, headers=headers)

    print("Pesapal Token Response:", response.status_code, response.text)  # Debugging

    return response.json().get("token")

def register_ipn():
    """Register IPN (Instant Payment Notification) URL"""
    token = get_access_token()
    print("Pesapal Access Token:", token)

    url = f"{BASE_URL}/api/URLSetup/RegisterIPN"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {"url": settings.PESAPAL_IPN_URL, "ipn_notification_type": "POST"}
    response = requests.post(url, json=data, headers=headers)
    return response.json()


from rest_framework.permissions import IsAuthenticated

class PesapalPaymentAPIView(APIView):
    """Handles Pesapal payments"""
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

    def post(self, request):
        # Extract user from the request
        user = request.user

        # Ensure booking exists and fetch the place details
        booking = Booking.objects.filter(user=user).last()  # Fetch the latest booking for the user
        if not booking:
            return Response({"error": "No booking found for the user"}, status=400)

        place = booking.place  # Fetch place from the booking

        token = get_access_token()
        ipn_response = register_ipn()
        ipn_id = ipn_response.get("ipn_id")

        merchant_reference = random.randint(1, 1000000000000000000)

        # Construct order data dynamically
        order_data = {
            "id": str(merchant_reference),
            "currency": "KES",  
            "amount": float(place.price),  
            "description": place.description,  
            "callback_url": settings.PESAPAL_CALLBACK_URL,
            "notification_id": ipn_id,
            "branch": place.name,  
            "billing_address": {
                "email_address": user.email,
                # "phone_number": user.phone_number,  
                # "country_code": user.country_code,  
                "first_name": user.first_name,
                # "middle_name": user.middle_name if user.middle_name else "",
                "last_name": user.last_name,
                # "line_1": user.address  
            }
        }

        # Make request to Pesapal
        url = f"{BASE_URL}/api/Transactions/SubmitOrderRequest"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(url, json=order_data, headers=headers)
        pesapal_response = response.json()

        # Debugging: Print full response
        print("Pesapal API Response:", pesapal_response) 

        if "redirect_url" not in pesapal_response:
            return Response({"error": "Failed to generate Pesapal payment link", "details": pesapal_response}, status=400)

        pesapal_button_html = f'''
        <form action="{pesapal_response['redirect_url']}" method="POST">
            <button type="submit" class="pesapal-button">Pay with Pesapal</button>
        </form>
        '''

        return Response({"pesapal_button_html": pesapal_button_html})

class PesapalTransactionStatusAPIView(APIView):
    """Check transaction status"""
    permission_classes = [AllowAny]

    def get(self, request):
        token = get_access_token()
        order_tracking_id = request.GET.get("OrderTrackingId")

        if not order_tracking_id:
            return Response({"error": "Missing OrderTrackingId"}, status=400)

        url = f"{BASE_URL}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        return Response(response.json())


@api_view(["POST"])
@permission_classes([AllowAny])
def pesapal_ipn(request):
    """Handle Pesapal IPN (Instant Payment Notification)"""
    data = request.data
    with open("ipn_log.json", "a") as log_file:
        json.dump(data, log_file)
        log_file.write("\n")
    return Response({"message": "IPN received"}, status=200)


# CONTACT US
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

import json
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Disable CSRF for API (use proper authentication in production)
def contact_us(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')

            if not name or not email or not message:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            subject = f"New Contact Us Message from {name}"
            recipients = ["pascalouma54@gmail.com", "owillypascal@gmail.com", "enceptics.vacay@gmail.com"]

            # **Admin Email Template (Styled)**
            admin_email_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                    .container {{ background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); }}
                    .header {{ background-color: #773697; color: #ffffff; padding: 10px; text-align: center; font-size: 20px; font-weight: bold; border-radius: 8px 8px 0 0; }}
                    .content {{ padding: 20px; color: #333; }}
                    .footer {{ margin-top: 20px; font-size: 12px; color: #666; text-align: center; }}
                    .bold-text {{ font-weight: bold; color: #773697; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        New Contact Us Message
                    </div>
                    <div class="content">
                        <p><span class="bold-text">Name:</span> {name}</p>
                        <p><span class="bold-text">Email:</span> {email}</p>
                        <p><span class="bold-text">Message:</span></p>
                        <p>{message}</p>
                    </div>
                    <div class="footer">
                        &copy; Enceptics Team
                    </div>
                </div>
            </body>
            </html>
            """

            # **User Confirmation Email Template (Styled)**
            user_email_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                    .container {{ background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); }}
                    .header {{ background-color: #773697; color: #ffffff; padding: 10px; text-align: center; font-size: 20px; font-weight: bold; border-radius: 8px 8px 0 0; }}
                    .content {{ padding: 20px; color: #333; }}
                    .footer {{ margin-top: 20px; font-size: 12px; color: #666; text-align: center; }}
                    .bold-text {{ font-weight: bold; color: #773697; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        Thank You for Contacting Us!
                    </div>
                    <div class="content">
                        <p>Dear <span class="bold-text">{name}</span>,</p>
                        <p>Thank you for reaching out to us! We have received your message and will get back to you as soon as possible.</p>
                        <p><span class="bold-text">Your Message:</span></p>
                        <p>{message}</p>
                        <p>Best Regards,</p>
                        <p>The Enceptics Team</p>
                    </div>
                    <div class="footer">
                        &copy; Enceptics | Helping You Succeed.
                    </div>
                </div>
            </body>
            </html>
            """

            # **Send Admin Notification Email**
            admin_email_message = EmailMultiAlternatives(
                subject,
                message,  # Plain text fallback
                settings.DEFAULT_FROM_EMAIL,
                recipients
            )
            admin_email_message.attach_alternative(admin_email_content, "text/html")
            admin_email_message.send()

            # **Send User Confirmation Email**
            user_email_message = EmailMultiAlternatives(
                "We've Received Your Message – Enceptics",
                "Thank you for contacting us. We will get back to you soon!",  # Plain text fallback
                settings.DEFAULT_FROM_EMAIL,
                [email]  # Send email to the user
            )
            user_email_message.attach_alternative(user_email_content, "text/html")
            user_email_message.send()

            return JsonResponse({'message': 'Message sent successfully!'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Custom Itenerary request

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.conf import settings
from .models import Place

@csrf_exempt
def notify_managers(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body or "{}")  # Ensure data is parsed safely

        user_name = data.get("name")
        user_email = data.get("email")
        selected_interests = data.get("interests", [])  # FIX: Ensure this is always a list
        
        if not user_name or not user_email or not selected_interests:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Find managers related to the selected interests
        managers = Place.objects.filter(category_type__in=selected_interests).values_list('manager__email', 'sub_manager__email')
        manager_emails = {email for pair in managers for email in pair if email}  # Remove None values

        # Email content
        subject = "New User Interest Notification"
        context = {
            'recipient_name': 'Manager',
            'message_body': f"A user has submitted an interest request:\n\nName: {user_name}\nEmail: {user_email}\nInterests: {', '.join(selected_interests)}",
            'action_url': 'https://enceptics.com/manager-dashboard',
            'current_year': 2025,
        }
        html_content = render_to_string('emails/notify_managers_template.html', context)
        text_content = strip_tags(html_content)

        # Send email to all relevant managers
        if manager_emails:
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, list(manager_emails))
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        # Send email to the system admin
        admin_context = context.copy()
        admin_context['recipient_name'] = 'Admin'
        admin_html_content = render_to_string('emails/notify_admin_template.html', admin_context)
        admin_text_content = strip_tags(admin_html_content)

        admin_msg = EmailMultiAlternatives(subject, admin_text_content, settings.DEFAULT_FROM_EMAIL, ["enceptics.vacay@gmail.com"])
        admin_msg.attach_alternative(admin_html_content, "text/html")
        admin_msg.send()

        # Email confirmation to the user
        user_subject = "Your Request Has Been Received"
        user_context = {
            'recipient_name': user_name,
            'message_body': f"Thank you for showing interest in our experiences! We have received your request for the following interests:\n{', '.join(selected_interests)}\n\nOur managers will review your request and get back to you soon.",
            'action_url': 'https://enceptics.com/user-dashboard',
            'current_year': 2025,
        }
        user_html_content = render_to_string('emails/user_confirmation_template.html', user_context)
        user_text_content = strip_tags(user_html_content)

        user_msg = EmailMultiAlternatives(user_subject, user_text_content, settings.DEFAULT_FROM_EMAIL, [user_email])
        user_msg.attach_alternative(user_html_content, "text/html")
        user_msg.send()

        return JsonResponse({"success": "Notifications sent successfully."})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)