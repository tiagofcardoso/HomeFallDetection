from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from time import sleep
from .config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO

def send_alert():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body="*Alert: Alguem esta caido na sala e passando mal!*",
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print(f"Message sent: {message.sid}")
        
    except TwilioRestException as e:
        print(f"Twilio error: {e}")