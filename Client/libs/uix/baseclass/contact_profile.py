import traceback

from kivy import platform
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from components.toast import toast
from plyer import filechooser

if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.permissions import check_permission



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
        return toast("Not implemented yet.")
        # self.manager.set_current("verify_identity")
        # verify_identity = self.manager.get_screen("verify_identity")
        # verify_identity.name_of_contact = str(self.title)

        # PDialog(content=IdentityCheck(image=self.image)).open()

    def change_p2p(self):
        return toast("Not implemented yet")

    def open_menu(self):
        self.popup2 = PDialog(content=Settings(title=self.title))
        self.popup2.open()

    def change_bg(self):
        if platform == "android":
            if not check_permission("android.permission.READ_MEDIA_IMAGES"):
                return request_permissions([Permission.READ_MEDIA_IMAGES, Permission.READ_MEDIA_VIDEO])

        try:
            filechooser.open_file(on_selection=self.selected_file, multiple=False)
        except Exception as _:
            print(traceback.format_exc())
            pass

    def selected_file(self, selection):
        if len(selection) == 0:
            return

        sel = selection[0]
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        file_extension = sel[sel.rfind('.'):].lower()
        t = file_extension in image_extensions
        if not t:
            self.toast("Unsupported ending.")
            return

        print(sel)

    def reset_bg(self):
        pass


class IdentityCheck(PBoxLayout):
    image = StringProperty()


class Settings(PBoxLayout):
    title = StringProperty()
