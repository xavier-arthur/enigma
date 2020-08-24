from os import mkdir
from os.path import exists as file_exists
from getpass import getpass
from pathlib import Path
from sys import exit as sys_exit
from json import loads as json_loads
from json import dumps as json_dumps
from traceback import print_exc
import base64

from cryptography.fernet import Fernet
import bcrypt

class Password:

    config_folder = f"{Path.home()}/.config/enigma"

    @staticmethod
    def rehash(data):
        # whenever the password changes this function makes sure that it user
        # information will be saved accordingly

        new_pass = Password.configure()

        if not file_exists(f"{Password.config_folder}/data.enc"):
            sys_exit(0)

        try:
            # without this checking this section makes it impossible to store a
            # new password hash
                with open(f"{Password.config_folder}/data.enc", "wb") as out:
                    out.write(JSHandler.encrypt(data, newpass=new_pass))
                    # encrypting with new password hash
        except:
            print_exc()

    @staticmethod
    def configure():
        """ creates a config file with the given password lock """

        if not file_exists(f"{Password.config_folder}"):
            mkdir(Password.config_folder)



        passw = getpass("new password:")
        passw2 = getpass("confirm new password:")

        if passw != passw2:
            print("passwords don't match,try again")
            sys_exit(1)

        with open(f"{Password.config_folder}/.enigma", "wb") as hsh:
            hsh.write(bcrypt.hashpw(f"{passw}".encode(), bcrypt.gensalt()))

        return passw


    @staticmethod
    def check_against(trial: bytes) -> bool:

        with open(f"{Password.config_folder}/.enigma", "rb") as hsh:
            key = hsh.read()

            if bcrypt.checkpw(trial, key):
                return True
            return False


class JSHandler:

    # Coding this made me question my existence

    def get_salt():

        if file_exists(f"{Password.config_folder}/.enigma-s"):
            with open(f"{Password.config_folder}/.enigma-s", "rb") as data_in:
                _salt = data_in.read()
        else:
            _salt = bcrypt.gensalt()
            with open(f"{Password.config_folder}/.enigma-s", "wb") as out:
                out.write(_salt)
        return _salt


    def newk(passw, salt):
        kdf = bcrypt.kdf(
            passw.encode(),
            salt,
            32,
            100
        )
        key = key = base64.urlsafe_b64encode(kdf)

        return key


    @staticmethod
    def encrypt(data: dict, newpass=None) -> bytes:

        if newpass:
            JSHandler.passw = newpass
            JSHandler._key = JSHandler.newk(newpass, JSHandler.get_salt())

        cipher = Fernet(JSHandler._key)

        data_byte = json_dumps(data).encode()
        encrypted_data = cipher.encrypt(data_byte)

        return encrypted_data


    @staticmethod
    def decrypt(data: "filepath") -> dict:

        cipher = Fernet(JSHandler._key)

        with open(data, "rb") as file_dec:
            data_dec = file_dec.read()

        data = cipher.decrypt(data_dec)

        data = json_loads(data)

        return data

    #passw = None
    # this variable is just here for documentation
    # when this class is called it uses _newk_ and _get_salt_
    # to recriate the original Fernet key created to store data
