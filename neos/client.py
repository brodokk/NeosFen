import dataclasses
import json
from datetime import datetime
from os import path as OSpath
from typing import Dict, List
from urllib.parse import ParseResult, urlparse

import dacite
from requests import Session
from dateutil.parser import isoparse

from . import __version__
from .classes import (
    LoginDetails,
    NeosDirectory,
    NeosFriend,
    NeosLink,
    NeosRecord,
    NeosUser,
    RecordType,
    recordTypeMapping,
    OnlineStatus,
    CurrentSessionAccessLevel,
    FriendStatus,
)
from .endpoints import CLOUDX_NEOS_API
from neos import exceptions as neos_exceptions

DACITE_CONFIG = dacite.Config(
    cast=[RecordType, OnlineStatus, CurrentSessionAccessLevel, FriendStatus],
    type_hooks={
        datetime: isoparse,
        ParseResult: urlparse,
    },
)

AUTHFILE_NAME = "auth.token"


@dataclasses.dataclass
class Client:
    userId: str = None
    token: str = None
    expirey: datetime = None
    secretMachineId: str = None
    session: Session = Session()


    @property
    def headers(self) -> dict:
        default = {"User-Agent": "neos.py/{__version__}"}
        if not self.userId or not self.token:
            print("WARNING: headers sections not set. this might throw an error soon...")
            return default
        default["Authorization"] = f"neos {self.userId}:{self.token}"
        return default

    @staticmethod
    def processRecordList(data: List[dict]):
        ret = []
        for raw_item in data:
            item = dacite.from_dict(NeosRecord, raw_item, DACITE_CONFIG)
            x = dacite.from_dict(recordTypeMapping[item.recordType], raw_item, DACITE_CONFIG)
            ret.append(x)
        return ret

    def _request(
            self, verb: str, path: str, data: dict = None, json: dict = None, params: dict = None
        ) -> Dict:
        args = {'url': CLOUDX_NEOS_API + path}
        if data: args['data'] = data
        if json: args['json'] = json
        if params: args['params'] = params
        func = getattr(self.session, verb, None)
        with func(**args) as req:
            print("[{}] {}".format(req.status_code, args))
            if req.status_code != 200:
                if "Invalid credentials" in req.text:
                    raise neos_exceptions.InvalidCredentials(req.text)
                else:
                    raise neos_exceptions.NeosAPIException(req.status_code, req.text)
            responce = req.json()
            if "message" in responce:
                raise neos_exceptions.NeosAPIException(responce["message"])
            return responce

    def login(self, data: LoginDetails) -> None:
        responce = self._request('post', "/userSessions",
            json=dataclasses.asdict(data))
        self.userId = responce["userId"]
        self.token = responce["token"]
        self.secretMachineId = responce["secretMachineId"]
        self.expirey = isoparse(responce["expire"])
        self.session.headers.update(self.headers)

    def loadToken(self):
        if OSpath.exists(AUTHFILE_NAME):
            with open(AUTHFILE_NAME, "r") as f:
                session = json.load(f)
                expirey = datetime.fromisoformat(session["expire"])
                if datetime.now().timestamp() < expirey.timestamp():
                    print("reading token from disk")
                    self.token = session["token"]
                    self.userId = session["userId"]
                    self.expirey = expirey
                    self.secretMachineId = session["secretMachineId"]
                    self.session.headers.update(self.headers)
                else:
                    raise neos_exceptions.NoTokenError
        else:
            raise neos_exceptions.NoTokenError

    def saveToken(self):
        with open(AUTHFILE_NAME, "w+") as f:
            json.dump(
                {
                    "userId": self.userId,
                    "expire": self.expirey.isoformat(),
                    "token": self.token,
                    "secretMachineId": self.secretMachineId,
                },
                f,
            )

    def neosDBSignature(self, iconUrl: str) -> str:
        return iconUrl.split("//")[1].split(".")[0]

    def neosDbToHttp(self, iconUrl: str) -> str:
        url = "https://cloudxstorage.blob.core.windows.net/assets"
        url = url + self.neosDBSignature(iconUrl)
        return url

    def getUserData(self, user: str = None) -> NeosUser:
        if user is not None:
            user = self.userId
            responce = self._request('get', "/users/" + user)
            return dacite.from_dict(NeosUser, responce, DACITE_CONFIG)

    def getFriends(self):
        """
        returns the friends you have.

        Note: does not create friends out of thin air. you need to do that yourself.
        """
        responce = self._request('get', f"/users/{self.userId}/friends")
        return [dacite.from_dict(NeosFriend, user, DACITE_CONFIG) for user in responce]

    def getInventory(self) -> List[NeosRecord]:
        """
        The typical entrypoint to the inventory system.
        """
        responce = self._request(
            'get',
            f"/users/{self.userId}/records",
            params={"path": "Inventory"},
        )
        return self.processRecordList(responce)

    def getDirectory(self, directory: NeosDirectory) -> List[NeosRecord]:
        """
        given a directory, return it's contents.
        """
        responce = self._request(
            'get',
            f"/users/{directory.ownerId}/records",
            params={"path": directory.content_path},
        )
        return self.processRecordList(responce)

    def resolveLink(self, link: NeosLink) -> NeosDirectory:
        """
        given a link type record, will return it's directory. directoy can be passed to getDirectory
        """
        _, user, record = link.assetUri.path.split("/")  # TODO: better
        responce = self._request(
            'get',
            f"/users/{user}/records/{record}",
        )
        return dacite.from_dict(NeosDirectory, responce, DACITE_CONFIG)
