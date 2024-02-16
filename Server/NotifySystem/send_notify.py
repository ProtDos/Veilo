import firebase_admin
from firebase_admin import credentials, messaging
firebase_cred = credentials.Certificate(r"D:\JugendForscht\Server\NotifySystem\veilo-924d5-firebase-adminsdk-4dgeh-b5c9d66d31.json")
firebase_app = firebase_admin.initialize_app(firebase_cred)


tk = "cUQI728kQ--klR7e84_WJQ:APA91bGyRG3aZ2zVrLWdkjQnlNm6FR5dj5An5Vs5IofszQaDlxwsXgLrGJceGVo6p8yWBBQBK5R3SHjjDGTKYcqqKFRzErqbBCUmQdesx-nGUerOsrjOZcIG3ToqiLvSDK8NhKJf8TkZ"


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
