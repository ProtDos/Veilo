import hashlib

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import DictProperty, ListProperty, StringProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from components.toast import toast
import rsa
import socket

from kivy.app import App

conn = "socket.protdos.com", 5002


def hash_obj(obj):
    hashed = hashlib.sha256(obj.encode())
    return hashed.hexdigest()


class Verify(PScreen):
    name_of_contact = StringProperty()

    public_own = StringProperty()
    public_contact = StringProperty()

    hashed_own = StringProperty()
    hashed_contact = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.okay, 0)

    def okay(self, dt):

        self.public_own = rsa.PublicKey.save_pkcs1(App.get_running_app().public_key).decode()
        print(self.public_own)

        so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        so.connect(conn)

        print("NAME: ", self.name_of_contact)

        so.send(f"GET_ID:{self.name_of_contact}".encode())
        resp = so.recv(1024).decode()
        print("ONE: ", resp)

        if resp != "error":
            so.close()
            so2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            so2.connect(conn)
            so2.send(f"GET_PUBLIC:{resp}".encode())
            resp2 = so2.recv(1024).decode()
            print("TWO: ", resp)
            if resp2 != "error":
                self.public_contact = resp2

        print("PUBLIC_CONTATC: ", self.public_contact)

        if self.public_own is not None and self.public_contact is not None:
            self.hashed_own = hash_obj(str(self.public_own))
            self.hashed_contact = hash_obj(str(self.public_contact))
            print("yey")
        else:
            toast("Error occurred")
            self.manager.set_current("auth")




