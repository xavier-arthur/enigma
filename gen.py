from random import randrange as rr
from random import choice
from pathlib import Path
from os.path import exists as file_exists

from encrypter import JSHandler

class DataBase:

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

    _folder_path = f"{Path.home()}/.config/enigma/data.enc"

    def __init__(self, username, provider):

        self.username = username
        self.provider = provider
        self.pwrd = self.generate()
        self.info = {provider: [username, self.pwrd]}

    def generate(self) -> str:
        pwrd = DataBase._chars[rr(27)] #sets the first ch to an alphabetic letter

        while len(pwrd) != 14: # passwd length here
            try:
                if rr(3) < 2:
                    pwrd += choice(DataBase._chars)
                else:
                    pwrd += choice(DataBase._chars).upper()
            except AttributeError:
                continue

        return self.check(pwrd)


    def check(self, pwrd) -> str:

        sym_count = 0
        syms = ("$", "^", "*", "%", "@", "?", ".", "!", "&")
        pwrd = list(pwrd)

        for obj in pwrd:
            if obj in syms:
                sym_count += 1

        target = rr(-1, 4)
        while sym_count < target:
            pwrd[rr(1, len(pwrd))] = choice(syms)
            sym_count += 1

        return "".join(pwrd)


    def write_to_file(self) -> list:

        if file_exists(DataBase._folder_path):
            file_content = JSHandler.decrypt(DataBase._folder_path)

            i = 2
            original = self.provider
            while self.provider in file_content:
                self.provider = f"{original}-{i}"
                i += 1

            self.info = {self.provider: [self.username, self.pwrd]}

        else:
            file_content = {}

        file_content.update(self.info)
        file_content_enc = JSHandler.encrypt(file_content)

        with open(DataBase._folder_path, "wb") as data:
            data.write(file_content_enc)

        return list(self.info[self.provider])


    @staticmethod
    def get_db() -> dict:
        #TODO   turn this into a generator
        """
        decrypts and returns a dict with everything
        """

        if file_exists(DataBase._folder_path):
            return JSHandler.decrypt(DataBase._folder_path)


    @staticmethod
    def remove_from_db(to_remove: "key"):

        #TODO   repetitive code
        data = DataBase.get_db()
        del data[to_remove]
        file_content_enc = JSHandler.encrypt(data)
        with open(DataBase._folder_path, "wb") as data:
            data.write(file_content_enc)
