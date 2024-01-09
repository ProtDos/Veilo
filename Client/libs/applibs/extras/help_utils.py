from jnius import autoclass
from kivy import platform
import locale


def get_android_system_language():
    try:
        if platform == "android":
            Locale = autoclass("java.util.Locale")
            Configuration = autoclass("android.content.res.Configuration")
            context = autoclass("org.kivy.android.PythonActivity").mActivity
            config = Configuration()
            config.setLocale(Locale.getDefault())
            context = context.createConfigurationContect(config)
            return context.getResources().getConfiguration().locale.language
        return locale.getdefaultlocale()[0].split('_')[0]
    except Exception as e:
        print(e)
        return "en"
