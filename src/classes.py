import json
import os
from datetime import datetime
from dataclasses import dataclass

from kivymd.app import MDApp

from neos import exceptions as neos_exceptions
from neos.classes import LoginDetails as NeosLoginDetails

from utilities import EnhancedJSONEncoder, CollisionsList

@dataclass
class NeosFenLogin:
    userId: str
    expire: str
    lastUpdate: datetime
    token: str
    secretMachineId: str

@dataclass
class NeosFenLogins:
    logins: CollisionsList[NeosFenLogin]
    save_file: str = os.getcwd() + "/savelogins"

    def _write_config(self):
        with open(self.save_file, 'w') as f:
            json.dump(self.logins, f, cls=EnhancedJSONEncoder)

    def _read_config(self):
        try:
            with open(self.save_file) as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return {}


    def clean_config(self):
        os.remove(self.save_file)

    def do_login(self, login, password):
        app = MDApp.get_running_app()


        login_details = {"password": password}
        if "@" in login:
            login_details['email'] = login
        elif login.startswith('U-'):
            login_details['ownerId'] = login
        else:
            login_details['username'] = login
        try:
            deets = NeosLoginDetails(**login_details)
        except neos_exceptions.NeosException as e:
            app.root.current_screen.ids['error_message'].text = str(e)
            return False
        try:
            app.neosFenClient.login(deets)
        except Exception as e:
            app.root.current_screen.ids['error_message'].text = str(e)
            return False

        neosFenLogin = NeosFenLogin(
            app.neosFenClient.userId,
            app.neosFenClient.expire.isoformat(),
            app.neosFenClient.lastUpdate,
            app.neosFenClient.token,
            app.neosFenClient.secretMachineId,
        )

        try:
            self.logins.append(neosFenLogin, "userId")
        except ValueError:
            self.logins.update("userId", neosFenLogin.userId, "token", neosFenLogin.token)

        self._write_config()
        return True

    def logout(self):
        app = MDApp.get_running_app()
        print(self.logins)
        self.logins.update("userId", self.neosFenConnectedUser["userId"], "token", "")
        print(self.logins)
        self._write_config()
        app.root.current = 'loginscreen'

    def load_config(self):
        app = MDApp.get_running_app()
        data = self._read_config()
        if data:
            session = data[0]
            self.logins.append(
                NeosFenLogin(
                    session["userId"],
                    datetime.fromisoformat(session["expire"]),
                    datetime.fromisoformat(session["lastUpdate"]),
                    session["token"],
                    session["secretMachineId"],
                ),
                "userId",
            )
            if not session["token"]:
                return False
            self.neosFenConnectedUser = session
            print("reading token from disk")
            app.neosFenClient.lastUpdate = datetime.fromisoformat(session["lastUpdate"])
            app.neosFenClient.token = session["token"]
            app.neosFenClient.userId = session["userId"]
            app.neosFenClient.expire = app.neosFenClient.expire
            app.neosFenClient.secretMachineId = session["secretMachineId"]
            app.neosFenClient.session.headers.update(app.neosFenClient.headers)
            return True
        return False

@dataclass
class NeosFenFriend:
    id: str
    icon: str

@dataclass
class NeosFenFriendsList:
    friends: CollisionsList[NeosFenFriend]


