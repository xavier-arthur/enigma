from os import mkdir
from os.path import exists as file_exists
from getpass import getpass
from pathlib import Path
from sys import exit as sys_exit
from json import loads as json_loads
from json import dumps as json_dumps

from cryptography.fernet import Fernet
import bcrypt

class Password:

    config_folder = f"{Path.home()}/.config/enigma"

    @staticmethod
    def configure():
    # creates a config file with the given password lock

        try:
            mkdir(Password.config_folder)
        except FileExistsError:
            old_pass = getpass("Insert your current password:")
            if not Password.check_against(old_pass):
                print("password incorrect")
                sys_exit(1)

        passw = getpass("Insert new password:")
        passw2 = getpass("Confirm new password:")

        if passw == passw2:
            with open(f"{Password.config_folder}/.enigma", "wb") as hsh:
                hsh.write(bcrypt.hashpw(f"{passw}".encode(),
                                        bcrypt.gensalt()))
            return passw


    @staticmethod
    def check_against(trial: str) -> bool:

        with open(f"{Password.config_folder}/.enigma", "rb") as hsh:
            key = hsh.read()

            if key == bcrypt.hashpw(trial.encode(), key):
                return True
            return False


class JSHandler:

    key = b'uM3KEXwsYrCYgac4aJMHjEispuRWnFQxwSAnv2pqFp4='
    cipher = Fernet(key)

    @staticmethod
    def encrypt(data: dict):
        """
        encrypts a json dict and returns it
        """

        data_byte = json_dumps(data).encode()
        data_enc = JSHandler.cipher.encrypt(data_byte)

        return data_enc


    @staticmethod
    def decrypt(data: "file path") -> dict:
        """
        decrypts a json dict and returns it
        """
        with open(data, "rb")as file_dec:
            data_dec = file_dec.read()

        data = JSHandler.cipher.decrypt(data_dec).decode()
        data = json_loads(data)

        return data
