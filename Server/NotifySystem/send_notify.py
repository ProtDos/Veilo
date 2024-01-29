import firebase_admin
from firebase_admin import credentials, messaging
firebase_cred = credentials.Certificate(r"D:\JugendForscht\Server\NotifySystem\veilo-924d5-firebase-adminsdk-4dgeh-b5c9d66d31.json")
firebase_app = firebase_admin.initialize_app(firebase_cred)


tk = "f755YuhBTjqtdaHuWMJJPH:APA91bFoJnQtNO0pgen7LMfr-Z2CTSH5PmMnbZ3vETD2Qn0mpogbMF13B_Ca7vhUjxXRZoWvTR5swJ3-E1dBtVYOhBvNI7uOzIuRhOqgEvbJgdxsLJDgZrFj31JKCi3oPTr1pK0COYVt"


def send_token_push(title, body, token):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token
    )

    response = messaging.send(message)

    print("Successfully sent message:", response)
    print(f"     [DEBUG] Token: {token}")


if __name__ == "__main__":
    send_token_push("New message!", "You have received a new message.", tk)

    # 1b1b2b
    # fbfbfb
