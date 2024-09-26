from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = 'enter_your_sid'
auth_token = 'enter_your_token'
client = Client(account_sid, auth_token)

def sendSMS(sender,recipient,body):
    message = client.messages \
                    .create(
                        body=body,
                        from_=sender,
                        to=recipient
                    )

    print(message.sid)