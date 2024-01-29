import os

path = r"D:\JugendForscht\Client\extensions\vault.dmk"


def set_dmk(secret: str, msg: str):
    secret = '"' + secret + '"'
    msg = '"' + msg + '"'
    os.system(f'dmk -v {path} set -e {secret} -t {msg}')


def get_dmk(secret: str):
    secret = '"' + secret + '"'
    os.system(f'dmk -v {path} get -e {secret}')


from kivy.app import App
from kivy.uix.button import Button


class SimpleKivyApp(App):
    def build(self):
        button = Button(text='Click me!', on_press=self.on_button_press)
        return button

    @staticmethod
    def on_button_press(_):
        set_dmk("Something", "Something 123")
        get_dmk("Something")
        print('Button pressed!')


if __name__ == '__main__':
    SimpleKivyApp().run()
