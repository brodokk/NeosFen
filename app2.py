import asyncio
from asyncio.tasks import Task
from datetime import datetime
from getpass import getpass
from typing import List
from collections import Counter
from neos import classes, client, exceptions

c = client.Client()

async def main():
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

    friends = await c.getFriends()
    print(type(friends[0]))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
