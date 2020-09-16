from random import randrange as rr
from random import choice
from pathlib import Path
from os.path import exists as file_exists
from json import loads as json_loads
from json import load as json_load
from traceback import print_exc

import pandas as pd

from encrypter import JSHandler

class DataManager:

    _chars = [
        "a", "b", "c", "d", "e",
        "f", "g", "h", "i", "j",
        "k", "l", "m", "n", "o",
        "p", "q", "r", "s", "t",
        "u", "v", "w", "x", "y",
        "z", "1", "2", "3", "4",
        "5", "6", "7", "8", "9",
        "0", "$", "^", "*", "%",
        "@", "?", ".", "!", "&"
    ]

    folder_path = f"{Path.home()}/.config/enigma/data.enc"

    def __init__(self, username: str, provider: str):

        self.username = username
        self.provider = provider
        self.pwrd = DataManager.__generate()
        self.info = {provider: [username, self.pwrd]}


    def write_to_file(self) -> list:
        """
        encrypts a DataManager object, writes to file and
        returns a list containing it's data
        """

        if file_exists(DataManager.folder_path):
            file_content = JSHandler.decrypt(DataManager.folder_path)

            i = 2
            original = self.provider
            while self.provider in file_content:
                self.provider = f"{original}-{i}"
                i += 1

            self.info = {self.provider: [self.username, self.pwrd]}
        else:
            file_content = {}

        file_content.update(self.info)
        file_content = dict(sorted(file_content.items()))
        file_content_enc = JSHandler.encrypt(file_content)

        with open(DataManager.folder_path, "wb") as data:
            data.write(file_content_enc)

        return list(self.info[self.provider])


    @classmethod
    def __check(cls, pwrd) -> str:

        sym_count = 0
        syms = cls._chars[36:]
        pwrd = list(pwrd)


        for ch in pwrd:
            sym_count += 1 if ch in syms else 0

        target = rr(-1, 4)
        while sym_count < target:
            pwrd[rr(1, len(pwrd))] = choice(syms)
            sym_count += 1

        return "".join(pwrd)


    @staticmethod
    def __generate() -> str:
        pwrd = DataManager._chars[rr(27)] #sets the first ch to an alphabetic letter

        while len(pwrd) != 14: # passwd length here
            try:
                if rr(3) < 2:
                    pwrd += choice(DataManager._chars)
                else:
                    pwrd += choice(DataManager._chars).upper()
            except AttributeError:
                continue

        return DataManager.__check(pwrd)


    @staticmethod
    def static_write(content: dict):
        """
        encrypts and writes a dict to disk
        """

        content = JSHandler.encrypt(content)

        with open(DataManager.folder_path, "wb") as out:
            out.write(content)


    @staticmethod
    def get_db() -> dict:
        """
        decrypts and returns a dict with everything
        """

        if file_exists(DataManager.folder_path):
            return JSHandler.decrypt(DataManager.folder_path)


    @staticmethod
    def remove_from_db(to_remove: "dict key"):
        """
        removes an entry of the dictionary by key
        """

        data = DataManager.get_db()
        del data[to_remove]
        DataManager.static_write(data)


    @staticmethod
    def importjson(json_file: "json filepath"):
        with open(json_file) as data_in:
            json_content = json_load(data_in)

        return json_content


    @staticmethod
    def import_csv(load: "str filepath"):
        df = pd.read_csv(load)
        data = df.to_json()
        data = json_loads(data)

        enigma_compat = {}

        for name, username, password in zip(
                data["name"].values(),
                data["username"].values(),
                data["password"].values()
            ):

            enigma_compat.update({name: [username, password]})

        return enigma_compat


    @staticmethod
    def change_password(provider: str, new_password: str):
        enigma_data = DataManager.get_db()
        enigma_data[provider][1] = new_password
        DataManager.static_write(enigma_data)


    @staticmethod
    def change_provider_name(provider: str, new_name: str):
        enigma_data = DataManager.get_db()
        enigma_data[new_name] = enigma_data.pop(provider)
        DataManager.static_write(enigma_data)
