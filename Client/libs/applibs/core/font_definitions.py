from kivy.core.text import LabelBase

fonts_path = "assets/fonts/"

fonts = [
    {
        "name": "Lexend",
        "fn_regular": fonts_path + "Lexend-Regular.ttf",
        "fn_bold": fonts_path + "Lexend-Bold.ttf",
    },
    {
        "name": "LexendThin",
        "fn_regular": fonts_path + "Lexend-Thin.ttf",
    },
    {
        "name": "LexendBold",
        "fn_regular": fonts_path + "Lexend-Bold.ttf",
    },
    {
        "name": "LexendLight",
        "fn_regular": fonts_path + "Lexend-Light.ttf",
    },
    {
        "name": "LexendMedium",
        "fn_regular": fonts_path + "Lexend-Medium.ttf",
    },
    {
        "name": "LexendRegular",
        "fn_regular": fonts_path + "Lexend-Regular.ttf",
    },
    {
        "name": "Icons",
        "fn_regular": fonts_path + "Feather.ttf",
    },
    {
        "name": "Iconly",
        "fn_regular": fonts_path + "iconly.ttf",
    },

    {
        "name": "PoppinsBold",
        "fn_regular": fonts_path + "Poppins-Bold.ttf",
    },
    {
        "name": "BPoppins",
        "fn_regular": fonts_path + "Poppins-Bold.ttf",
    },
    {
        "name": "PoppinsLight",
        "fn_regular": fonts_path + "Poppins-Light.ttf",
    },
    {
        "name": "PoppinsMedium",
        "fn_regular": fonts_path + "Poppins-Medium.ttf",
    },
{
        "name": "MPoppins",
        "fn_regular": fonts_path + "Poppins-Medium.ttf",
    },
    {
        "name": "PoppinsRegular",
        "fn_regular": fonts_path + "Poppins-Regular.ttf",
    },
    {
        "name": "PoppinsSemiBold",
        "fn_regular": fonts_path + "Poppins-SemiBold.ttf",
    },
]


def register_fonts():
    for font in fonts:
        LabelBase.register(**font)
