import os
import json
from kivy.app import App
from components.toast import toast
from components.screen import PScreen
from kivy.properties import ListProperty, BooleanProperty
from core.encryption import encrypt, decrypt


class GroupMembers(PScreen):
    member_list = ListProperty([{"text": "Test", "secondary_text": "Test 123", "checked": False}, {"text": "Test2", "secondary_text": "Test 123", "checked": True}])
    original = ListProperty([{"text": "Test", "secondary_text": "Test 123", "checked": False}, {"text": "Test2", "secondary_text": "Test 123", "checked": True}])
    search_bar = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ps = App.get_running_app().unhashed_password

        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(App.get_running_app().my_file_path)),
                                            'assets/users.json')), 'r') as f:
            self.data = json.load(f)

        if self.data != {}:
            for i in self.data:
                i_dec = decrypt(i, ps)
                if i_dec is not None and i_dec != App.get_running_app().username:
                    user_data = {
                        "text": i_dec,
                        "secondary_text": decrypt(self.data[i]["message"], ps),
                        "checked": False,
                    }
                    self.member_list.append(user_data)
                    self.original.append(user_data)

        self.ids.field.bind(text=self.on_text)

    def on_text(self, _, value):
        if value:
            value = value.lower()
            for item in self.original:
                if value not in item["text"].lower():
                    try:
                        self.member_list.remove(item)
                    except:
                        pass
                else:
                    if item not in self.member_list:
                        self.member_list.append(item)
        else:
            self.member_list = self.original

    def show_searchbar(self):
        if self.search_bar:
            self.search_bar = False
            self.ids.field.text = ""
        else:
            self.search_bar = True

    def back(self):
        self.manager.set_current("home", side="right")

    def continue_group(self):
        checked_items = [item for item in self.member_list if item.get("checked", False)]
        if checked_items:
            for item in checked_items:
                print(item)
            toast("Creating groups isn't supported yet.")
        else:
            toast("Please provide at least one more participant.")

    def check_click(self, instance):

        position_dict = []

        layout_manager = self.ids.grid

        for index, child in enumerate(layout_manager.children):
            position_dict.append({"index": index, "pos": child.pos})

        for item in position_dict:
            if item["pos"] == instance.pos:

                data_item = self.member_list[::-1][int(item['index'])]

                if data_item["checked"]:
                    data_item["checked"] = False
                else:
                    data_item["checked"] = True

        self.ids.aaaa.refresh_from_data()
