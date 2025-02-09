from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from authentication.models import Place, Booking, Payment
from django_daraja.mpesa.core import MpesaClient
import time

class MpesaPaymentView(APIView):
    """
    Endpoint for making M-Pesa payments
    """

    def post(self, request, *args, **kwargs):
        print("MpesaPaymentView is executed")  # Debug: Check if the view is executed

        # Fetch the relevant data from the request
        place_id = request.data.get("id")  # Extract place_id from the request data
        user_id = request.data.get('user_id', None)  # Extract user_id from the request data

        # Retrieve the associated Booking for the Place (assuming a ForeignKey relationship)
        if user_id is not None:
            booking = Booking.objects.filter(place=place_id, user=user_id).first()
            if booking:
                phone_number = booking.phone
                print('Customer\'s phone number:', phone_number)
            else:
                return Response({"success": False, "msg": "Booking not found for the place or user"}, status=404)
        else:
            return Response({"success": False, "msg": "User ID is not provided"}, status=400)

        print("Received place_id:", place_id)  # Debug: Print the received place_id
        print("Received user_id:", user_id)  # Debug: Print the received user_id

        place = get_object_or_404(Place, id=place_id)  # Fetch the Place object by its ID

        # Extract the price from the Place object
        price_string = place.price  # Example string representing a number
        price = int(price_string)
        print('price for this place is', price)

        # Perform the M-Pesa payment request with retry logic
        cl = MpesaClient()
        amount = price  # You might need to convert the price to the required format
        account_reference = 'Enceptics'  # Customize as needed
        transaction_desc = 'Vacation'  # Customize as needed
        callback_url = 'https://mydomain.com/mpesa-payments/daraja/'  # Customize your callback URL

        response = self.make_mpesa_payment_with_retry(cl, phone_number, amount, account_reference, transaction_desc, callback_url)

        print("M-Pesa API Response Content:")
        print("mpesa response:", response.content)

       # Handle the response and return it to the client
        # Handle the response and return it to the client
        response_data = response.json()  # Assuming the response is in JSON format

        response_code = response_data.get("ResponseCode")
        response_description = response_data.get("ResponseDescription")

        if response_code == "0" and response_description == "Success. Request accepted for processing":
            # Update the associated Payment model to mark the payment as complete
            payment, created = Payment.objects.get_or_create(booking=booking)
            payment.is_complete = True
            payment.payment_id = response_data.get("MerchantRequestID")  # Store the payment ID
            payment.save()

            # Update the booking status or any other relevant data
            booking.status = "Paid"
            booking.save()
            return Response({"success": True, "msg": "M-Pesa payment initiated successfully", "response": response_data}, status=201)
        
        elif response_code == "1032" and response_description == "Request canceled by user.":
            # Handle the case where the user canceled the payment
            return Response({"success": False, "msg": "User canceled the payment"}, status=400)

        
        else:
            return Response({"success": False, "msg": "M-Pesa payment initiation failed"}, status=400)

        
    def make_mpesa_payment_with_retry(self, cl, phone_number, amount, account_reference, transaction_desc, callback_url):
        max_retries = 3
        retry_delay = 20  # 60 seconds

        for retry in range(max_retries):
            response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
            print(f"Attempt {retry + 1} - M-Pesa API Response Content:")
            print(response.content)

            if response.status_code == 200:
                return response
            else:
                print(f"Service is temporarily unavailable. Retrying in {retry_delay} seconds.")
                time.sleep(retry_delay)

        return None  # Return None if max retries are reached without success
