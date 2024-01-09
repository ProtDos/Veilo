from kivy.core.window import Window
from kivy.app import App
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen


def find_item_before(lst, target_item):
    for i in range(1, len(lst)):
        if lst[i] == target_item:
            return lst[i - 1]
    return None


class V2FA(PScreen):
    sad_dia = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.bind(on_keyboard=self.check_backslash)

        self.v1_num = None
        self.v2_num = None
        self.v3_num = None
        self.v4_num = None
        self.v5_num = None
        self.v6_num = None

        self.final = None

        self.current = None

        self.l = [self.ids.v1, self.ids.v2, self.ids.v3, self.ids.v4, self.ids.v5, self.ids.v6]

        self.ids.v1.focus = True
        self.ids.verify_button.disabled = True

    def check_backslash(self, _, key, *__):
        if key == 8:
            try:
                self.current.text = ""
                self.current.disabled = False
                self.current.focus = True

                i = find_item_before(self.l, self.current)
                self.current = i

                self.ids.verify_button.disabled = True

            except:
                pass
        elif key == 271:
            if self.final is not None and len(self.final) == 6:
                self.verify_pin()

    def v1(self, num):
        self.final = None

        self.v1_num = num
        self.ids.v1.disabled = True
        self.ids.v2.disabled = False

        self.ids.v2.focus = True

        self.current = self.ids.v1

    def v2(self, num):
        self.v2_num = num
        self.ids.v2.disabled = True
        self.ids.v3.disabled = False

        self.ids.v3.focus = True

        self.current = self.ids.v2

    def v3(self, num):
        self.v3_num = num
        self.ids.v3.disabled = True
        self.ids.v4.disabled = False

        self.ids.v4.focus = True

        self.current = self.ids.v3

    def v4(self, num):
        self.v4_num = num
        self.ids.v4.disabled = True
        self.ids.v5.disabled = False

        self.ids.v5.focus = True

        self.current = self.ids.v4

    def v5(self, num):
        self.v5_num = num
        self.ids.v5.disabled = True
        self.ids.v6.disabled = False

        self.ids.v6.focus = True

        self.current = self.ids.v5

    def v6(self, num):
        self.v6_num = num
        self.ids.v6.disabled = True

        self.final = str(self.v1_num) + str(self.v2_num) + str(self.v3_num) + str(self.v4_num) + str(self.v5_num) + str(self.v6_num)

        self.ids.verify_button.disabled = False

        self.current = self.ids.v6

    def verify_pin(self):
        pin = self.final
        self.ids.verify_button.disabled = True

        App.get_running_app().verify_2fa(pin)

    def open_sad(self):
        self.sad_dia = PDialog(content=LostDialog())
        self.sad_dia.open()


class LostDialog(PBoxLayout):
    @staticmethod
    def close_dia():
        App.get_running_app().root.get_screen("2fa_verify").sad_dia.dismiss(force=True)
        App.get_running_app().root.set_current("auth")
