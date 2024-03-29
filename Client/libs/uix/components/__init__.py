from kivy.factory import Factory

r = Factory.register

r("PButton", module="libs.uix.components.button")
r("PIconButton", module="libs.uix.components.button")
r("PIconButton2", module="libs.uix.components.button")

r("PLabel", module="libs.uix.components.label")
r("PIcon", module="libs.uix.components.label")

r("PTextField", module="libs.uix.components.textfield")

r("PBoxLayout", module="libs.uix.components.boxlayout")

r("PToolbar", module="libs.uix.components.toolbar")
r("PToolbar_Chat", module="libs.uix.components.toolbar")

r("PScreen", module="libs.uix.components.screen")

r("FitImage", module="libs.uix.components.image")

r("ChatListItem", module="libs.uix.components.listitem")
r("ListItem", module="libs.uix.components.listitem")
r("ListItemSwitch", module="libs.uix.components.listitem")

r("ChatBubble", module="libs.uix.components.chat_bubble")
r("ChatBubble2", module="libs.uix.components.chat_bubble")
r("ChatBubble3", module="libs.uix.components.chat_bubble")
r("Message", module="libs.uix.components.chat_bubble")
r("AudioMessage", module="libs.uix.components.chat_bubble")
r("Attachment", module="libs.uix.components.chat_bubble")
r("ImageMessage", module="libs.uix.components.chat_bubble")
r("General", module="libs.uix.components.chat_bubble")
