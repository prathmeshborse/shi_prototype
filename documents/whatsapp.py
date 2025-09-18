#Create a Django View to Send WhatsApp Messages

from twilio.rest import Client
from django.http import JsonRespons

# Twilio credentials
TWILIO_ACCOUNT_SID = 'ACc171356a051ca40b0dedecfa1217a749'
TWILIO_AUTH_TOKEN = 'b88891da23e8702b5c4bb9115a2b69f6'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Twilio sandbox number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(request):
    to_number = 'whatsapp:+917061107730'  # Replace with the recipient's number
    message_body = 'Hello from your Django WhatsApp integration!'

    message = client.messages.create(
        body=message_body,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number
    )

    return JsonResponse({'status': 'sent', 'sid': message.sid})


