import asyncio
from asyncio.tasks import Task
from datetime import datetime
from getpass import getpass
from typing import List
from collections import Counter
from neos import classes, client, exceptions

from kivy.app import App
from kivy.uix.button import Button
import asynckivy as ak

c = client.Client()

def heavy_task(n, w):
    import time
    for i in range(n):
        time.sleep(1)
        print('heavy task:', i, w)

async def main():
    have_auth = False
    try:
        c.loadToken()
        have_auth = True
    except exceptions.NoTokenError:
        pass

    if not have_auth:
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

    friends = await c.getFriends()
    print(type(friends[0]))

class TestApp(App):

    def build(self):
        return Button(font_size='20sp')

    def on_start(self):
        await main()
        async def some_task():
            button = self.root
            button.text = 'start heavy task'
            await ak.event(button, 'on_press')
            button.text = 'running...'
            await ak.run_in_thread(lambda: heavy_task(5, 'a'))
            await ak.run_in_thread(lambda: heavy_task(5, 'b'))
            button.text = 'done'
        ak.start(some_task())



if __name__ == "__main__":
    TestApp().run()
