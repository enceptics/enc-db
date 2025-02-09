# utils.py

import random
import string
import requests
from django.utils.text import slugify

from django.conf import settings


# Existing utility functions

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.body)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=random_string_generator(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug

# This is your updated geocoding function
def get_coordinates_from_place_name(place_name, api_key):
    try:
        # Construct the URL with latitude and longitude as query parameters
        url = "https://api.api-ninjas.com/v1/geocoding"
        params = {
            "city": place_name,  # Use place_name as the city
            "country": "",  # You can include the country if needed
        }

        # Include your API key in the headers
        headers = {
            "x-api-key": api_key,
        }

        # Make the request to API Ninjas
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if response.status_code == 200:
            # Check if the response is a list of locations
            if isinstance(data, list) and len(data) > 0:
                # Extract the latitude and longitude from the first location in the list
                location = data[0]
                latitude = location.get("latitude", 0.0)
                longitude = location.get("longitude", 0.0)
                return {"latitude": latitude, "longitude": longitude}
            else:
                print("No location data found for the place.")
        else:
            print("Error in geocoding:", data.get("message"))
    except Exception as e:
        print("Geocoding error:", str(e))
    return None




# ANOTHER PAYPAL EXAMPLE

import requests
import json
from decouple import config

def make_paypal_payment(formatted_price, currency, return_url, cancel_url):
    
    # Set up PayPal API credentials
    client_id = config("PAYPAL_SANDBOX_CLIENT_ID")
    print('my paypal client_id', client_id)
    secret = config("PAYPAL_SANDBOX_CLIENT_SECRET")
    print('my paypal secret', secret)

    # Set up API endpoints
    base_url = "https://api.sandbox.paypal.com"
    token_url = base_url + '/v1/oauth2/token'
    payment_url = base_url + '/v1/payments/payment'

    # Request an access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(client_id, secret), data=token_payload, headers=token_headers)

    if token_response.status_code != 200:
        return False, "Failed to authenticate with PayPal API", None

    access_token = token_response.json()['access_token']

    # Create payment payload
    payment_payload = {
     'intent': 'sale',
     'payer': {'payment_method': 'paypal'},
     'transactions': [{
         'amount': {
             'total': formatted_price,  # Use formatted_price as it's already a string
             'currency': currency,
         },
         'description': 'Vulnvision scan & protect',
     }],
     'redirect_urls': {
         'return_url': return_url,
         'cancel_url': cancel_url,
     }
    }



    # Create payment request
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_response = requests.post(payment_url, data=json.dumps(payment_payload), headers=payment_headers)
    print(payment_response.text)
    if payment_response.status_code != 201:
        return False , 'Failed to create PayPal payment.',None

    payment_id = payment_response.json()['id']
    approval_url = next(link['href'] for link in payment_response.json()['links'] if link['rel'] == 'approval_url')

    return True,payment_id, approval_url


def verify_paypal_payment(payment_id):
    # Set up PayPal API credentials
    client_id = getattr(settings, "PAYPAL_SANDBOX_CLIENT_ID")
    secret = getattr(settings, "PAYPAL_SANDBOX_CLIENT_SECRET")
    url = getattr(settings, "PAYPAL_BASE_URL") 

    # Set up API endpoints
    base_url = url
    token_url = base_url + '/v1/oauth2/token'
    payment_url = base_url + '/v1/payments/payment'

    # Request an access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(client_id, secret), data=token_payload, headers=token_headers)

    if token_response.status_code != 200:
        raise Exception('Failed to authenticate with PayPal API.')

    access_token = token_response.json()['access_token']

    # Retrieve payment details
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_details_url = f'{payment_url}/{payment_id}'
    payment_details_response = requests.get(payment_details_url, headers=payment_headers)

    if payment_details_response.status_code != 200:
        raise Exception('Failed to retrieve PayPal payment details.')

    payment_status = payment_details_response.json()['state']
    if payment_status == 'approved':
        # Payment is successful, process the order
        # Retrieve additional payment details if needed
        payer_email = payment_details_response.json()['payer']['payer_info']['email']
        # ... process the order ...
        return True
    else:
        # Payment failed or was canceled
        return False

# END ANOTHER


# New utility function 
# I'll probably use this later for google geocoodinates

# def get_coordinates_from_place_name(place_name, google_api_key):
#     try:
#         response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params={
#             'address': place_name,
#             'key': google_api_key,
#         })

#         data = response.json()
#         if response.status_code == 200:
#             results = data.get('results', [])
#             if results:
#                 location = results[0].get('geometry', {}).get('location', {})
#                 latitude = location.get('lat', 0.0)
#                 longitude = location.get('lng', 0.0)
#                 return {'latitude': latitude, 'longitude': longitude}
#         else:
#             print('Error in geocoding:', data.get('error_message'))
#     except Exception as e:
#         print('Geocoding error:', str(e))
#     return None
