from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from time import sleep
from .config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO


def send_alert(message=None):
    # Verificar se as credenciais estão configuradas
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO]):
        print("Error: Twilio credentials not properly configured")
        print("Please check your .env file and ensure all Twilio variables are set")
        return

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        if message is None:
            message = "ALERT: Fall detected! Person needs help!"

        # Tentar enviar a mensagem
        message = client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print(f"Message sent successfully: {message.sid}")

    except TwilioRestException as e:
        print(f"Twilio error: {str(e)}")
        print("\nPlease verify your Twilio credentials:")
        print(f"Account SID: {TWILIO_ACCOUNT_SID[:6]}...{TWILIO_ACCOUNT_SID[-4:] if TWILIO_ACCOUNT_SID else 'Not Set'}")
        print(f"Auth Token: {'*' * 8}{TWILIO_AUTH_TOKEN[-4:] if TWILIO_AUTH_TOKEN else 'Not Set'}")
        print(f"From Number: {TWILIO_FROM or 'Not Set'}")
        print(f"To Number: {TWILIO_TO or 'Not Set'}")
    except Exception as e:
        print(f"Unexpected error sending alert: {str(e)}")
