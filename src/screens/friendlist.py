import os
import threading
import requests
from functools import partial
from time import sleep
from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.screen import MDScreen

from neos.classes import OnlineStatus
from neos.exceptions import NeosAPIException
from kivy.uix.button import Button
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock

from kivymd.uix.list import ImageLeftWidget, ThreeLineAvatarListItem, IconLeftWidget, MDList

from dataclasses import dataclass
from utilities import html2bbcode, CollisionsList
from datetime import datetime

from classes import NeosFenFriendsList, NeosFenFriend

class CustomThreeLineAvatarListItem(ThreeLineAvatarListItem):

    def __init__(self, id, **args):
        self.id = id
        super().__init__(**args)

class LoadingBoxLayout(MDBoxLayout):

    def hide_widget(self, dohide=True):

        if hasattr(self, 'saved_attrs'):
            if not dohide:
                self.height, self.size_hint_y, self.opacity, self.disabled = self.saved_attrs
                del self.saved_attrs
        elif dohide:
            self.saved_attrs = self.height, self.size_hint_y, self.opacity, self.disabled
            self.height, self.size_hint_y, self.opacity, self.disabled = 0, None, 0, True


class FriendsListScreen(MDScreen):

    updateThread = None
    stopThread = False
    runningThread = False

    def get_image(self, userIconUrl):
        app = MDApp.get_running_app()
        userIcons_directory = app.user_data_dir + '/cache/userIcons'

        if(not os.path.exists(userIcons_directory)):
            os.makedirs(userIcons_directory)

        userIconName = userIconUrl.split("assets/")[1]
        userIconPath = userIcons_directory + "/" + userIconName + ".webp"

        if not os.path.exists(userIconPath):
            img_data = requests.get(userIconUrl).content
            with open(userIconPath, 'wb') as handler:
                handler.write(img_data)

        return userIconPath

    def get_data(self, friend):
        username = friend.friendUsername
        onlineStatus = friend.userStatus.onlineStatus
        if friend.userStatus.onlineStatus == OnlineStatus.OFFLINE:
            return
            # Optimization, dont show offline user for the moment since not
            # usefull
            onlineStatus = "[color=bdc3c7]OFFLINE[/color]"
        elif friend.userStatus.onlineStatus == OnlineStatus.ONLINE:
            onlineStatus = "[color=2ecc71]ONLINE[/color]"
        elif friend.userStatus.onlineStatus == OnlineStatus.AWAY:
            onlineStatus = "[color=f39c12]AWAY[/color]"
        elif friend.userStatus.onlineStatus == OnlineStatus.BUSY:
            onlineStatus = "[color=e74c3c]BUSY[/color]"
        else:
            raise ValueError('Unknow online status')
        sessionName = "  "
        sessionInfo = "  "
        if friend.userStatus.onlineStatus != OnlineStatus.OFFLINE:
            sessionName = "In "
            if friend.userStatus.currentSession:
                sessionName += html2bbcode(
                    friend.userStatus.currentSession.name)
                sessionInfo = "{} session with {} users".format(
                    friend.userStatus.currentSessionAccessLevel,
                    friend.userStatus.currentSession.activeUsers,
                )
            else:
                sessionName += "Private world"


        return username, onlineStatus, sessionName, sessionInfo

    def refresh(self):
        if self.runningThread:
            self.stopThread = True
            while self.runningThread:
                sleep(1)
        self.ids.friendlist.clear_widgets()
        self.build_list()

    def on_pre_enter(self):
        self.ids.loading_status.hide_widget(False)

    def on_enter(self):
        self.build_list()

    def update_friendslist(
        self, username, onlineStatus, sessionName, sessionInfo, friend, icon, *args
    ):
        list_item = CustomThreeLineAvatarListItem(
            text=username + " - " + onlineStatus,
            secondary_text=sessionName,
            tertiary_text=sessionInfo,
            id=friend.id,
        )
        list_item.add_widget(ImageLeftWidget(
            source = icon,
            radius = [25]
        ))
        self.ids.friendlist.add_widget(list_item)

    def build_list(self):
        self.runningThread = True
        updateThread = threading.Thread(target=self._build_list)
        updateThread.start()

    def _build_list(self):
        app = MDApp.get_running_app()
        try:
            friends = app.neosFenClient.getFriends()
        except NeosAPIException:
            app.neosFenLogins.logout()
            self.runningThread = False
            self.stopThread = False
            return
        current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self.ids.last_refresh.text = f"{current_time}"
        self.ids.connected_contacts.text = f"0 on {len(friends)} online"
        app.friends = friends
        online = 0
        for friend in friends:
            if self.stopThread:
                continue
            Clock.schedule_once(partial(self.ids.loading_status.hide_widget))
            try:
                username, onlineStatus, sessionName, sessionInfo = self.get_data(friend)
                if not app.neosFenFriendsList.friends.contains("id", friend.id):
                    user = app.neosFenClient.getUserData(friend.id)
                    if user.profile:
                        icon = app.neosFenClient.neosDbToHttp(user.profile.iconUrl)
                    else:
                        icon = app.installed_path + "/ressources/imgs/default_icon.png"
                    app.neosFenFriendsList.friends.append(
                        NeosFenFriend(user.id, icon),
                        "id",
                    )
                else:
                    icon = app.neosFenFriendsList.friends.get("id", friend.id).icon
                    if not icon:
                        icon = app.installed_path + "/Untitled-1.png"
                online += 1
                self.ids.connected_contacts.text = f"{online} on {len(friends)} online"
            except TypeError:
                continue
            Clock.schedule_once(partial(self.update_friendslist, username, onlineStatus, sessionName, sessionInfo, friend, icon))
        self.ids.connected_contacts.text = f"{online} on {len(friends)} online"
        if self.stopThread:
            self.ids.connected_contacts.text = f"0 on 0 online"
            self.ids.friendlist.clear_widgets()
        self.runningThread = False
        self.stopThread = False

    def on_leave(self):
        print("bye")

    def disconnect(self):
        app = MDApp.get_running_app()
        if self.runningThread:
            self.stopThread = True
            while self.runningThread:
                sleep(1)
        self.ids.friendlist.clear_widgets()
        self.manager.transition = SlideTransition(direction="right")
        app.neosFenLogins.clean_config()
        self.manager.current = 'loginscreen'
        self.manager.get_screen('loginscreen').resetForm()
