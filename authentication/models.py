from django.db import models
from django.utils.text import slugify
from django.conf import settings
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .utils import unique_slug_generator
from django.utils import timezone
import requests
from django.http import JsonResponse
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from accounts.models import User
from django.conf import settings
from accounts.models import User
from django.utils.timezone import now

# booking

TYPE = (
    ('OWJ', 'One way journey'),
    ('TWJ', 'Two way journey')
)

def room_images_upload_path(instance, file_name):
    return f"{instance.place_slug}/room_cover/{file_name}"

def room_display_images_upload_path(instance, file_name):
    return f"{instance.room.room_slug}/room_display/{file_name}"


class HeroSection(models.Model):

    image_index = models.IntegerField(default=0)
    hero_text = models.CharField(max_length=255, default="Choose Your Purpose: Culinary Delights, Thrilling Sports, Cultural Journeys, and More!")
    image1 = models.ImageField(upload_to='hero_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='hero_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='hero_images/', blank=True, null=True)

    def __str__(self):
        return self.hero_text

class Customer(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.customer

from django.contrib.auth.models import User  # If you want to associate bookings with users

class Room(models.Model):
    name = models.CharField(max_length=50)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=3)
    room_slug = models.SlugField()
    is_booked = models.BooleanField(default=False)
    capacity = models.IntegerField()
    room_size = models.CharField(max_length=5)
    cover_image = models.ImageField(upload_to=room_images_upload_path)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

from django.db import models
from django.conf import settings

class Place(models.Model):
    CATEGORY_CHOICES = [
        ('micro_adventure', 'Micro Adventure'),
        ('group_booking', 'Group Booking'),
        ('culinary_tours', 'Culinary Tours'),
        ('farmers_markets', 'Farmers Markets'),
        ('nature_hikes', 'Nature Hikes'),
        ('art_workshops', 'Art Workshops'),
        ('cultural_festivals', 'Cultural Festivals'),
        ('historical_tours', 'Historical Tours'),
        ('community_service', 'Community Service'),
        ('outdoor_adventures', 'Outdoor Adventures'),
        ('wellness_retreats', 'Wellness Retreats'),
        ('local_sports_events', 'Local Sports Events'),
        ('music_and_dance_classes', 'Music and Dance Classes'),
        ('local_artisan_tours', 'Local Artisan Tours'),
        ('themed_photo_walks', 'Themed Photo Walks'),
        ('wildlife_spotting', 'Wildlife Spotting'),
        ('cultural_exchange', 'Cultural Exchange'),
        ('storytelling_nights', 'Storytelling Nights'),
        ('virtual_reality', 'Virtual Reality'),
        ('family_fun', 'Family Fun'),
        ('explore_the_unknown', ' Explore the Unknown'),
        ('sustainable_travels', 'Sustainable Travels'),
        ('custom_itineraries', 'Custom Itineraries'),
    ]

    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='manager')
    sub_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='sub_manager')
    name = models.CharField(max_length=150)
    category_type = models.CharField(max_length=255, choices=CATEGORY_CHOICES, null=True, blank=True)
    description = models.TextField()
    duration = models.CharField(max_length=255, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    size = models.CharField(max_length=255, null=True, blank=True)
    cover_image = models.ImageField(upload_to='place_cover_images/')
    destination = models.TextField(null=True, blank=True)
    pictures = models.ImageField(upload_to='place_info_pictures/', null=True, blank=True)
    videos = models.FileField(upload_to='place_info_videos/', blank=True, null=True)
    weather_forecast = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    # Rating and reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    # New fields for statistics
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_bookings = models.PositiveIntegerField(default=0)
    total_visitors = models.PositiveIntegerField(default=0)

    # Booking statistics
    total_pending_bookings = models.PositiveIntegerField(default=0)
    total_completed_bookings = models.PositiveIntegerField(default=0)
    total_canceled_bookings = models.PositiveIntegerField(default=0)

    # Forecast data
    booking_trend = models.JSONField(default=list)  # Store booking trends as a list
    revenue_forecast = models.JSONField(default=list)  # Store revenue forecasts as a list

    def __str__(self):
        return self.name

class Review(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # Ratings out of 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user} for {self.place.name}'

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} just booked {self.place} for Ksh {self.place.price} from {self.checkin_date} to {self.checkout_date}'

    def save(self, *args, **kwargs):
        if not self.checkin_date:
            # If checkin_date is not provided, set it to the current date
            self.checkin_date = timezone.now().date()
        if not self.checkout_date:
            # If checkout_date is not provided, set it to 2 days after checkin_date
            self.checkout_date = self.checkin_date + timezone.timedelta(days=2)
        super(Booking, self).save(*args, **kwargs)

# payment

class Payment(models.Model):
    payment_id = models.CharField(max_length=255)  # Add this field to store the PayPal payment ID
    status = models.CharField(max_length=50, default="pending")

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,  # Cascade delete when the associated booking is deleted
        default=None,  # Specify a callable function as the default
        null=True,  # Allow the booking field to be NULL
    )

    is_complete = models.BooleanField(default=False)

    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.booking},  Payment status, [{self.is_complete}]'

class ExtraCharge(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)  # e.g., 'Kids' or 'Adults'
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Extra charges for {self.booking} is {self.amount} for {self.type}'

class PlaceInfo(models.Model):
    destination = models.OneToOneField(Place, on_delete=models.CASCADE, related_name='more_information')
    pictures = models.ImageField(upload_to='place_info_pictures/')
    videos = models.FileField(upload_to='place_info_videos/', blank=True, null=True)
    weather_forecast = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Description for {self.destination.name}"

class CheckIn(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=14, null=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return self.room.room_slug

class CheckOut(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    check_out_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer

class RoomDisplayImages(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    display_images = models.ImageField(upload_to=room_display_images_upload_path)

    def __str__(self):
        return self.room.room_slug

class About(models.Model):
    desc = models.TextField()
    mission=models.TextField()
    vision = models.TextField()

    def __str__(self):
        return self.desc

# Contract
class Contract(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Associate contract with user
    content = models.TextField()  # Store the contract text
    signed_at = models.DateTimeField(null=True, blank=True)  # Timestamp when signed
    is_signed = models.BooleanField(default=False)  # Check if signed
    signature = models.TextField(null=True, blank=True)  # Store signature (base64 or text)
    contract_image = models.ImageField(upload_to='contracts/', null=True, blank=True)  

    def __str__(self):
        return f"Contract for {self.user.first_name} {self.user.first_name} - {self.user.email}- {'Signed' if self.is_signed else 'Pending'}"





