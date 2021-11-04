#!/bin/python

import requests
from termcolor import colored


url = "https://api.neos.com/api/userSessions"

payload = {
    "username": "brodokk",
    "password": "Lp!Ds8@w",
}

#r = requests.post(url, json=payload)

#print(r.status_code)

#print(r.text)
#
data = {
    "userId": "U-brodokk",
    "token": "V2-Jv0kYVWX+xJbKQkORwFwyE_MbQr3YGYIM9H+x9t5Vcgnqw2Xu3HinVAL6mCHV7+rB7oiguewBniuQny9vaCcOu+CCsA54hEwp9XPgXEto8ns7H_D5lWF0Dp5jNifLTrXNo73pFGV+EMxBQrCULnetw+5jPqSI_fHidpaXEgSKZM=",
    "created": "2021-11-03T14:57:53.1834111Z",
    "expire": "2021-11-04T14:57:53.1834112Z",
    "rememberMe": False,
    "sourceIP": "82.65.48.226",
    "partitionKey": "U-brodokk",
    "rowKey": "V2-Jv0kYVWX+xJbKQkORwFwyE_MbQr3YGYIM9H+x9t5Vcgnqw2Xu3HinVAL6mCHV7+rB7oiguewBniuQny9vaCcOu+CCsA54hEwp9XPgXEto8ns7H_D5lWF0Dp5jNifLTrXNo73pFGV+EMxBQrCULnetw+5jPqSI_fHidpaXEgSKZM=",
    "timestamp": "2021-11-03T14:57:53.1948195+00:00",
    "eTag": "W/\"datetime'2021-11-03T14%3A57%3A53.1948195Z'\""
}

user = "U-brodokk"

url = "https://api.neos.com/api/users/" + user + "/friends"

r = requests.get(url, headers={'Authorization': 'neos ' + data["userId"] + ":" + data["token"]})
print(r.status_code)
print(r.text)

data = r.json()
for user in data:
    status = user["userStatus"]['onlineStatus']
    if status == "Online":
        status = colored(status, 'green')
    elif status == "Away":
        status = colored(status, 'yellow')
    elif status == "Busy":
        status = colored(status, 'red')
    elif status == "Offline":
        status = colored(status, 'white')
    else:
        status = colored(status, 'grey')
    print(user["id"] + ": " + status)
