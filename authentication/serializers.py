from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists
from rest_framework import serializers

from .models import  About, Room, CheckIn, Place, PlaceInfo, Booking, Payment, Review, HeroSection

class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        adapter = get_adapter()
        user = adapter.authenticate(self.context['request'], username=data.get('username'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is not active.")

        return user

    # booking


# class RoomSerializer(serializers.ModelSerializer):
#     category_name = serializers.CharField(source='category.category_name')

#     class Meta:
#         model = Room
#         fields = '__all__'

#     def create(self, validated_data):
#         return super().create(self.category_name)

class HeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        fields = '__all__'  # Serialize all fields

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        errors = {}

        # Add validation logic for each field
        checkin_date = data.get('checkin_date')
        checkout_date = data.get('checkout_date')
        phone = data.get('phone')
        email = data.get('email')
        is_paid = data.get('is_paid')
        user = data.get('user')
        place = data.get('place')

        # Example validation for checkin_date and checkout_date
        if not checkin_date:
            errors['checkin_date'] = 'Check-in date is required.'
        if not checkout_date:
            errors['checkout_date'] = 'Check-out date is required.'

        # You can add similar validation for other fields

        if errors:
            raise serializers.ValidationError(errors)

        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    # Add explicit validation for rating
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be an integer between 1 and 5.")
        return value

    def update(self, instance, validated_data):
        cover_image = validated_data.pop('cover_image', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if cover_image is not None:
            instance.cover_image = cover_image
        instance.save()
        return instance

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            # Construct the absolute URL for the image
            return self.context['request'].build_absolute_uri(obj.cover_image.url)
        return None

class PlaceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceInfo
        fields = '__all__'

    def update(self, instance, validated_data):
        pictures = validated_data.pop('pictures', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if pictures is not None:
            instance.cover_image = pictures
        instance.save()
        return instance

    def get_pictures_url(self, obj):
        if obj.pictures:
            # Construct the absolute URL for the image
            return self.context['request'].build_absolute_uri(obj.pictures.url)
        return None




class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class CheckinSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source='room.pk')
    room_slug = serializers.SlugField(source='room.room_slug')
    customer_id = serializers.IntegerField(source='customer.pk')
    customer_name = serializers.CharField(source='customer.username')

    class Meta:
        model = CheckIn
        fields = ('phone_number', 'email', 'customer_id', 'customer_name', 'room_id', 'room_slug',)

        # blog

class AboutSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ( 'desc', 'mission', 'vision',)
        model = About