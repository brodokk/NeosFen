import os
import sys
import pathlib

from kivy.core.window import Window
from kivy.config import Config
from kivy.resources import resource_add_path
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager

from kivymd.app import MDApp

from neos import exceptions as neos_exceptions
from neos import classes

from classes import NeosFenLogins, NeosFenFriendsList, NeosFenClient
from utilities import EnhancedJSONEncoder, CollisionsList, load_kv_files
from screens.friendlist import FriendsListScreen
from screens.login import LoginScreen

Window.size = (400, 600)

# Fix linux shit, maybe
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.write()

load_kv_files(pathlib.Path('src/kv'))


class NeosFenApp(MDApp):

    neosFenLogins = NeosFenLogins(CollisionsList())
    neosFenFriendsList = NeosFenFriendsList(CollisionsList())
    neosFenConnectedUser = None
    neosFenFriends = []
    neosFenClient = NeosFenClient()
    kv_directory = '/kv/'
    installed_path = os.path.dirname(os.path.realpath(__file__))

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.material_style = "M3"

        screenManager = ScreenManager()

        screenManager.add_widget(LoginScreen(name='loginscreen'))
        screenManager.add_widget(FriendsListScreen(name='friendslistscreen'))

        return screenManager

    def on_start(self):

        if self.neosFenLogins.load_config():
            self.root.current = 'friendslistscreen'

    def get_application_config(self):
        if(not self.username):
            return super(NeosFenApp, self).get_application_config()

        conf_directory = self.user_data_dir + '/' + self.username

        if(not os.path.exists(conf_directory)):
            os.makedirs(conf_directory)

        return super(NeosFenApp, self).get_application_config(
            '%s/config.cfg' % (conf_directory)
        )

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    NeosFenApp().run()
