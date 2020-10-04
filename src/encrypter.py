from os.path import exists as file_exists
from os import mkdir
from pathlib import Path
from getpass import getpass
from sys import exit as sys_exit
from json import loads as json_loads
from json import dumps as json_dumps
import base64

from cryptography.fernet import Fernet
import bcrypt

CONFIG_FOLDER = f"{Path.home()}/.config/enigma"

class Password:
    """
    methods belonging to the master password, not to be confused with the latter
    class
    """

    @staticmethod
    def configure():
        """ creates a config file with the given password lock """

        if not file_exists(f"{CONFIG_FOLDER}"):
            mkdir(CONFIG_FOLDER)

        passw = getpass("new password:")
        passw2 = getpass("confirm new password:")

        if passw != passw2:
            print("passwords don't match,try again")
            sys_exit(1)

        with open(f"{CONFIG_FOLDER}/.enigma", "wb") as hsh:
            hsh.write(bcrypt.hashpw(f"{passw}".encode(), bcrypt.gensalt()))

        return passw


    @staticmethod
    def check_against(trial: bytes) -> bool:
        """ compare password hashes """

        with open(f"{CONFIG_FOLDER}/.enigma", "rb") as hsh:
            key = hsh.read()

            if bcrypt.checkpw(trial, key):
                return True
            return False


class JSHandler:
    """
    this class contains necessary methods to handle the encryption of user's
    information, bear in mind that before encrypting the data is made into a
    JSON dict
    """

    @classmethod
    def rehash(cls, data):
        """
        whenever the password changes this function makes sure that it user
        information will be saved accordingly, however it has to be called
        explicitily, you should prefer using this over Password.configure
        unless you know what you're doing
        """

        new_pass = Password.configure()

        if not file_exists(f"{CONFIG_FOLDER}/data.enc"):
            sys_exit(0)

        # without this checking this section makes it impossible to store a
        # new password hash
        with open(f"{CONFIG_FOLDER}/data.enc", "wb") as out:
            out.write(cls.encrypt(data, newpass=new_pass))
            # encrypting with new password hash

    # Coding this made me question my existence

    @staticmethod
    def get_salt() -> bytes:
        """
        gets salt if saved otherwise creates a new one and writes it
        """

        if file_exists(f"{CONFIG_FOLDER}/.enigma-s"):
            with open(f"{CONFIG_FOLDER}/.enigma-s", "rb") as data_in:
                _salt = data_in.read()
        else:
            _salt = bcrypt.gensalt()
            with open(f"{CONFIG_FOLDER}/.enigma-s", "wb") as out:
                out.write(_salt)

        return _salt


    @classmethod
    def newk(cls, passw: bytes) -> "key":
        """ this generates a key based on user's password """
        # kdf stands for Key Derivation Function

        salt = cls.get_salt()
        kdf = bcrypt.kdf(
            passw.encode(),
            salt,
            32, # number of key bytes
            100 # number of rounds, the higher the better (and slower)
        )
        key = base64.urlsafe_b64encode(kdf)

        return key


    @classmethod
    def encrypt(cls, data: dict, newpass=None) -> bytes:
        """ encrypts "data" parameters then returns it """

        if newpass:
            cls.passw = newpass
            cls._key = cls.newk(newpass)

        cipher = Fernet(cls._key)

        data_byte = json_dumps(data).encode()
        encrypted_data = cipher.encrypt(data_byte)

        return encrypted_data


    @classmethod
    def decrypt(cls, data: "filepath") -> dict:
        """ gets the content of data.enc and returns it as a dict """

        cipher = Fernet(cls._key)

        with open(data, "rb") as file_dec:
            data_dec = file_dec.read()

        data = cipher.decrypt(data_dec)

        data = json_loads(data)

        return data

    # i used staticmehods because i wrote the entire program without giving the
    # due attention to this cryptography part and when i had it done didn't want
    # to change all of its logic
    # when this class is called it uses _newk and _get_salt
    # to recriate the original Fernet key created to store data
    # see method docstring for further instruction
