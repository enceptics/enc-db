import requests
from django.http import JsonResponse
from django.conf import settings
from authentication.utils import get_coordinates_from_place_name

from urllib.parse import quote

def get_weather(request, place_name):
    if request.method == 'GET':
        try:
            # Encode the place name
            place_name_encoded = quote(place_name)

            # Retrieve the API key from settings
            ambee_api_key = getattr(settings, 'AMBEE_WEATHER_API_KEY', None)
            api_ninjas_api_key = getattr(settings, 'API_NINJAS_API_KEY', None)

            # Check if the API keys are defined
            if ambee_api_key is None or api_ninjas_api_key is None:
                return JsonResponse({'error': 'API keys not defined'}, status=500)

            # Get the latitude and longitude for the specified place using API Ninjas geocoding
            coordinates = get_coordinates_from_place_name(place_name, api_ninjas_api_key)

            # Check if coordinates were found
            if coordinates is None:
                return JsonResponse({'error': 'Coordinates not found for the place'}, status=404)

            # Extract latitude and longitude from the coordinates
            latitude = coordinates.get('latitude', 0.0)
            longitude = coordinates.get('longitude', 0.0)

            # Construct the full URL with the API key
            ambee_url = f'https://api.ambeedata.com/weather/latest/by-lat-lng?lat={latitude}&lng={longitude}&x-api-key={ambee_api_key}'

            # Make a request to the Ambee Weather API
            ambee_response = requests.get(ambee_url)

            if ambee_response.status_code != 200:
                return JsonResponse({'error': 'Weather data not found'}, status=404)

            # Parse the JSON response from the API
            ambee_data = ambee_response.json()

            # Extract temperature in Fahrenheit from Ambee Weather API response
            temperature_fahrenheit = ambee_data['data']['temperature']

            # Convert Fahrenheit to Celsius and round to 2 decimal places
            temperature_celsius = round((temperature_fahrenheit - 32) * 5/9, 2)

            # Add the temperature in both Fahrenheit and Celsius to the weather_data dictionary
            weather_data = {
                'summary': ambee_data['data']['summary'],
                'icon': ambee_data['data']['icon'],
                'temperature_fahrenheit': round(temperature_fahrenheit, 2),
                'temperature_celsius': temperature_celsius,
                'humidity': ambee_data['data']['humidity'],
                'apparentTemperature': ambee_data['data']['apparentTemperature'],
                'dewPoint': ambee_data['data']['dewPoint'],
                'pressure': ambee_data['data']['pressure'],
                'windSpeed': ambee_data['data']['windSpeed'],
                'windGust': ambee_data['data'].get('windGust'),
                'windBearing': ambee_data['data']['windBearing'],
                'cloudCover': ambee_data['data']['cloudCover'],
                'precipIntensity': ambee_data['data'].get('precipIntensity'),
                'precipType': ambee_data['data'].get('precipType'),
                'uvIndex': ambee_data['data']['uvIndex'],
                'visibility': ambee_data['data']['visibility'],
            }

            return JsonResponse(weather_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




# # CAN BE USED LATER
# def get_weather(request, place_name):
#     if request.method == 'GET':
#         try:
#             # Retrieve the API key from settings
#             ambee_api_key = getattr(settings, 'AMBEE_WEATHER_API_KEY', None)
#             google_api_key = getattr(settings, 'GOOGLE_GEOCOODING_API_KEY', None)  # Add your Google Geocoding API key here
#             print(google_api_key)
#             # Check if the API keys are defined
#             if ambee_api_key is None or google_api_key is None:
#                 return JsonResponse({'error': 'API keys not defined'}, status=500)

#             # Get the latitude and longitude for the specified place using Google Geocoding
#             latitude, longitude = get_coordinates_from_place_name(place_name, google_api_key)

#             # Check if coordinates were found
#             if latitude is None or longitude is None:
#                 return JsonResponse({'error': 'Coordinates not found for the place'}, status=404)

#             # Construct the complete API URL for Ambee Weather
#             ambee_url = f'https://api.ambeedata.com/latest/by-lat-lng?lat={latitude}&lng={longitude}'

#             # Define headers for the Ambee Weather API request
#             ambee_headers = {
#                 'Content-Type': 'application/json',
#                 'x-api-key': ambee_api_key,
#                 'Accept-Language': 'en-US',  # Replace with your preferred language code
#             }

#             # Make a request to the Ambee Weather API
#             ambee_response = requests.get(ambee_url, headers=ambee_headers)
#             ambee_data = ambee_response.json()

#             if ambee_response.status_code == 200:
#                 # Extract relevant weather data from Ambee Weather API response
#                 weather_data = {
#                     'summary': ambee_data.get('summary', ''),
#                     'icon': ambee_data.get('icon', ''),
#                     'temperature': ambee_data.get('temperature', 0.0),
#                     'apparentTemperature': ambee_data.get('apparentTemperature', 0.0),
#                     'dewPoint': ambee_data.get('dewPoint', 0.0),
#                     'humidity': ambee_data.get('humidity', 0.0),
#                     'pressure': ambee_data.get('pressure', 0.0),
#                     'windSpeed': ambee_data.get('windSpeed', 0.0),
#                     'windGust': ambee_data.get('windGust', None),  # Optional field
#                     'windBearing': ambee_data.get('windBearing', 0),
#                     'cloudCover': ambee_data.get('cloudCover', 0.0),
#                     'precipIntensity': ambee_data.get('precipIntensity', None),  # Optional field
#                     'precipType': ambee_data.get('precipType', None),  # Optional field
#                     'uvIndex': ambee_data.get('uvIndex', 0),
#                     'visibility': ambee_data.get('visibility', 0.0),
#                 }
#                 return JsonResponse(weather_data)
#             else:
#                 return JsonResponse({'error': 'Weather data not found'}, status=404)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)



# #  open wether - can be used

# import requests
# from django.http import JsonResponse
# from django.conf import settings
# from authentication.utils import get_coordinates_from_place_name

# def get_weather(request, place_name):
#     if request.method == 'GET':
#         try:
#             # Retrieve the API key from settings
#             openweathermap_api_key = getattr(settings, 'OPENWEATHERMAP_API_KEY', None)
            
#             # Check if the OpenWeatherMap API key is defined
#             if openweathermap_api_key is None:
#                 return JsonResponse({'error': 'OpenWeatherMap API key not defined'}, status=500)

#             # Get the latitude and longitude for the specified place using API Ninjas geocoding
#             api_ninjas_api_key = getattr(settings, 'API_NINJAS_API_KEY', None)
#             coordinates = get_coordinates_from_place_name(place_name, api_ninjas_api_key)

#             # Check if coordinates were found
#             if coordinates is None:
#                 return JsonResponse({'error': 'Coordinates not found for the place'}, status=404)

#             # Extract latitude and longitude from the coordinates
#             latitude = coordinates.get('latitude', 0.0)
#             longitude = coordinates.get('longitude', 0.0)

#             # Define the exclude parameter to exclude hourly and daily forecasts
#             exclude = "hourly,daily"

#             # Define the OpenWeatherMap API URL with the API key and exclude parameter
#             openweathermap_url = f'https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&exclude={exclude}&appid={openweathermap_api_key}'

#             # Make a request to the OpenWeatherMap API
#             openweathermap_response = requests.get(openweathermap_url)

#             if openweathermap_response.status_code != 200:
#                 print("OpenWeatherMap API Error:", openweathermap_response.status_code)
#                 print("Response Content:", openweathermap_response.text)
#                 return JsonResponse({'error': 'Weather data not found'}, status=404)

#             # Parse the JSON response from the API
#             openweathermap_data = openweathermap_response.json()

#             # Extract relevant weather data from OpenWeatherMap API response
#             current_weather = openweathermap_data.get('current', {})
#             weather_data = {
#                 'description': current_weather.get('weather', [{}])[0].get('description', ''),
#                 'icon': current_weather.get('weather', [{}])[0].get('icon', ''),
#                 'temperature': current_weather.get('temp', 0.0),
#                 'humidity': current_weather.get('humidity', 0.0),
#                 'pressure': current_weather.get('pressure', 0.0),
#                 'windSpeed': current_weather.get('wind_speed', 0.0),
#                 'windDirection': current_weather.get('wind_deg', 0),
#                 'cloudiness': current_weather.get('clouds', 0),
#             }

#             return JsonResponse(weather_data)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)











