from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from components.toast import toast


class ContactProfile(PScreen):
    title = StringProperty()
    image = StringProperty()
    about = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.check_block, 0)

    def check_block(self, dt):
        if App.get_running_app().username == self.title:
            self.ids.block_screen.opacity = 0
            self.ids.block_screen.disabled = True
        else:
            self.ids.block_screen.opacity = 1
            self.ids.block_screen.disabled = False

    def verify(self):
        self.manager.set_current("verify_identity")
        verify_identity = self.manager.get_screen("verify_identity")
        verify_identity.name_of_contact = str(self.title)

        # PDialog(content=IdentityCheck(image=self.image)).open()

    def change_p2p(self):
        toast("Not implemented yet")
        pass

    def open_menu(self):
        self.popup2 = PDialog(content=Settings(title=self.title))
        self.popup2.open()


class IdentityCheck(PBoxLayout):
    image = StringProperty()


class Settings(PBoxLayout):
    title = StringProperty()
