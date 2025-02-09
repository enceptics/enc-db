from rest_framework.response import Response
from rest_framework.views import APIView
import json
import logging
from enceptics_views import MpesaGateWay

# Configure logging settings (you can adjust these settings as needed)
logging.basicConfig(level=logging.INFO,  # Set the log level to INFO
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class MpesaCallBack(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=200)

    def post(self, request, *args, **kwargs):
        logging.info("Callback from MPESA")  # Log an INFO-level message
        data = request.body

        # Define and initialize the 'gateway' instance here
        gateway = MpesaGateWay()  # Replace with your actual initialization code

        return gateway.callback(json.loads(data))
