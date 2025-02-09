# def generate_password(shortcode, passkey, timestamp):
#   """Generates mpesa api password using the provided shortcode and passkey"""
#   password_str = shortcode + passkey + timestamp
#   password_bytes = password_str.encode("ascii")
#   return base64.b64encode(password_bytes).decode("utf-8")

# def stk_push_request(payload):
#     request = payload["request"]
#     data = payload["data"]
#     amount = data["amount"]
#     phone_number = data["phone_number"] # A valid phone number with the format 254000000000
#     desc = data["description"] # This can be anything but not blank.
#     reference = data["reference"] # This can be anything but not blank.
    
#     # The shortcode and passkey values below are the test credential availed by safaricom.
#     shortcode = "174379" 
#     passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
#     timestamp = now.strftime("%Y%m%d%H%M%S")
    
#     password = generate_password(shortcode, passkey)
#     timestamp = env("timestamp")
#     checkout_url = https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest
#     c2b_callback = env("c2b_callback") # Endpoint where Mpesa will post the result
    
#     req_data = {
#         "BusinessShortCode": shortcode,
#         "Password": password,
#         "Timestamp": timestamp,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": math.ceil(float(amount)),
#         "PartyA": phone_number,
#         "PartyB": shortcode,
#         "PhoneNumber": phone_number,
#         "CallBackURL": c2b_callback,
#         "AccountReference": "Test",
#         "TransactionDesc": "Test",
#     }

#     res = requests.post(
#         checkout_url, json=req_data, headers=headers, timeout=30
#     )
#     res_data = res.json()
#     logging.info("Mpesa request data {}".format(req_data))
#     logging.info("Mpesa response info {}".format(res_data))

#     if res.ok:
#         data["ip"] = request.META.get("REMOTE_ADDR")
#         data["checkout_request_id"] = res_data["CheckoutRequestID"]

#         Transaction.objects.create(**data)
#     return res_data