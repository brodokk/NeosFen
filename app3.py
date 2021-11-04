import asyncio
from asyncio.tasks import Task
from datetime import datetime
from getpass import getpass
from typing import List
from collections import Counter
from neos import classes, client, exceptions


from kivy.app import App
from kivy.lang.builder import Builder

c = client.Client()

kv = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        ToggleButton:
            id: btn1
            group: 'a'
            text: 'Sleeping'
            allow_no_selection: False
            on_state: app.get_friends()
    Label:
        id: label
        status: 'Reading'
        text: app.friends
'''


async def _get_friends(friends, timeout=30):
    print('test', flush=True)
    data = await c.getFriends()
    friends = "uwu"
    print(data, flush=True)

def between_callback(args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(_get_friends(args.friends))
    loop.close()

class AsyncApp(App):

    neos_client = None
    friends = ""

    def build(self):
        return Builder.load_string(kv)

    def get_friends(self):
        import threading
        _thread = threading.Thread(target=self.between_callback, args=(self.friends))
        _thread.start()

    def app_func(self):
        '''This will run both methods asynchronously and then block until they
        are finished
        '''
        self.neos_client = asyncio.ensure_future(self.neos_login())

        async def run_wrapper():
            # we don't actually need to set asyncio as the lib because it is
            # the default, but it doesn't hurt to be explicit
            await self.async_run(async_lib='asyncio')
            print('App done')
            self.neos_client.cancel()

        return asyncio.gather(run_wrapper(), self.neos_client)

    async def getFriends(self):
        return self.neos_client.getFriends()

    async def neos_login(self):
        have_auth = False
        try:
            c.loadToken()
            have_auth = True
        except exceptions.NoTokenError:
            pass

        if not have_auth:
            print(
                "Please provide your Neos Login Details."
                "\n This data goes to the neos server, to get a token."
                "\n While typing your password, no input will appear. This is intentional.\n"
            )
            login = input("Username / Email: ")
            password = getpass()
            login_details = {"password": password}
            if "@" in login:
                login_details['email'] = login
            elif login.startswith('U-'):
                login_details['ownerId'] = login
            else:
                login_details['username'] = login
            deets = classes.LoginDetails(**login_details)
            try:
                await c.login(deets)
            except Exception as e:
                print(e)
                print("it seems that that login was invalid :(")
                exit(-1)
            data = input(
                f"Would you like to store your token to your harddrive? this token will expire naturally at {c.expirey}"
            )
            if data.lower() in ["true", "1", "t", "y", "yes", "yeah", "yup"]:
                print("saving token..")
                c.saveToken()

        return c

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncApp().app_func())
    loop.close()
