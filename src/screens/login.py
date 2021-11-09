from kivy.uix.screenmanager import SlideTransition

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

class LoginScreen(MDScreen):

    def do_login(self, login, password):
        app = MDApp.get_running_app()
        if not app.neosFenLogins.do_login(login, password):
            return
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'friendslistscreen'

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""
