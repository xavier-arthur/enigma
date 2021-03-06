#!/usr/bin/env python3
""" main method and some auxiliars functions"""

from os.path import exists as file_exists
from json import dump as json_dumps
from sys import exit as sys_exit
from getpass import getpass
import argparse as ap
import re

from pyperclip import copy

from password_handler import DataManager
from encrypter import Password, JSHandler
from encrypter import CONFIG_FOLDER

def get_args():
    """ returns parsed args """

    args = ap.ArgumentParser(description="Command line password mananger")

    args.add_argument("--configure", action="store_true",
                      help="changes default password")

    args.add_argument("action", default="display", nargs="?",
                      choices=["get", "add", "remove", "display", "importcsv",
                               "importjson", "export"])

    args.add_argument("data", type=str, nargs="*", metavar="PROVIDER"
                      + " USERNAME / csv/json FILEPATH",
                      help="info that will be feeded to selected action"
                      + " and username")

    args.add_argument("-y", "--auto-confirm", action="store_true",
                      help="don't ask for confirmation")

    args.add_argument("-c", "--copy", action="store_true",
                      help="sends password output to clipboard")

    args.add_argument("-m", "--manual-password", action="store_true",
                      default=None,
                      help="don't generate a password automatically")

    args.add_argument("--rename", action="store", type=str, nargs=2,
                      help="renames a service provider", metavar=("OLD", "NEW"))

    args.add_argument("-cp", "--change-password", action="store", type=str,
                      help="chances the password of given service provider",
                      nargs=1, metavar="PROVIDER")

    parsed = args.parse_args()

    if file_exists(f"{CONFIG_FOLDER}/.enigma"):
        pwtry = getpass("password:")
        if Password.check_against(pwtry.encode()):
            JSHandler.passw = pwtry
            JSHandler._key = JSHandler.newk(pwtry)
        else:
            print("invalid")
            sys_exit(2)
    elif not parsed.configure:
        print("configuration file not found, did you mean to --configure?")
        sys_exit(1)

    if parsed.manual_password:
        parsed.manual_password = getpass("new password for {}:"
                                         .format(parsed.data[0]))

    if parsed.configure:
        JSHandler.rehash(DataManager.get_db())
        sys_exit(0)

    if parsed.change_password:
        DataManager.change_password(
            parsed.change_password[0],
            getpass("new password for {}:".format(parsed.change_password[0]))
            )
        sys_exit(0)
    elif parsed.rename:
        DataManager.change_provider_name(
            parsed.rename[0],
            parsed.rename[1]
            )
        sys_exit(0)

    return parsed

def main():
    """
    checks which args where given and
    directs to execution to the rigth functions
    """

    global ARGS
    ARGS = get_args()
    # args is defined as a global variable so functions don't need parameters #

    content = globals()[ARGS.action]()
    # runs the function passed to args.action, if none were passed
    # "display" is executed. */

    if ARGS.copy:
        # sends the password to the clipboard
        try:
            copy(content[1])
        except IndexError:
            print("nothing to copy")
    elif ARGS.action == "get":
        print("Username:{}\nPassword:{}".format(content[0], content[1]))


def remove():
    """ deletes give login,provider,passowrd from DB """

    for i, obj in enumerate(ARGS.data):
        try:
            if not ARGS.auto_confirm:
                dict_key = get()
                if input(f"delete user {dict_key[0]} at {ARGS.data[0]}? [y/*] ") != "y":
                    continue

            DataManager.remove_from_db(obj)
            ARGS.data[0] = ARGS.data[i + 1]
            # └-> this  is done in order to loop through all arguments that were
            # feed to DATA at the very end it will raise an IndexError which is
            # expected and can be ignored
        except KeyError:
            print(f"provider {ARGS.data[0]} not found")
            continue
        except IndexError:
            pass


def get() -> list:
    """  decodes and returns a list with user and password in this order """

    data_dict = DataManager.get_db()

    matches = re.findall(f"{ARGS.data[0]}-?[0-9]?", str(data_dict.keys()))


    # this uses a regex matcher to get providers with similar name of the given
    # one and only runs if there are multiple matches
    if len(matches) > 1 and not ARGS.action == "remove":
        print(f"{len(matches)} entries found\n")
        for i, obj in enumerate(matches):
            print(f"{i + 1} -> {obj} at " + "{}".format(data_dict[obj][0]))

        entry = _entry_range(range(len(matches)))
        return list(data_dict[matches[entry]])
    try:
        return list(data_dict[ARGS.data[0]])
    except KeyError:
        print("provider not found, was it spelled right?")
        sys_exit(1)


def add() -> list:
    """ adds a new user with given password to DB """

    new_password = DataManager(ARGS.data[1], ARGS.data[0])

    if ARGS.manual_password:
        new_password.pwrd = ARGS.manual_password

    if ARGS.auto_confirm:
        confirm = "y"
    else:
        confirm = input(f"user {new_password.username} added"
                        + f" for provider {new_password.provider} created"
                        + " add to library? [y/*] ")

    return new_password.write_to_file() if confirm == "y" else sys_exit(0)

def display():
    """
    lists all providers and usernames for them at screen
    """

    data = DataManager.get_db()
    spaces = max(map(len, (map(str, data.keys()))))
    # converts all data.keys to str then gets the higher length off them all
    # which will further be used as number of spaces to format the list output

    for i in data.keys():
        print("{:<{}} @ {:>}".format(str(i), spaces, str(data[i][0])))

def importcsv():
    """
    adds data of a csv file to library (tested only with chromium browsers)
    """

    csv_content = DataManager.import_csv(ARGS.data[0])

    if file_exists(DataManager.folder_path):
        csv_content.update(DataManager.get_db())

    DataManager.static_write(csv_content)

def importjson():

    json_content = DataManager.importjson(ARGS.data[0])

    if file_exists(DataManager.folder_path):
        json_content.update(DataManager.get_db())

    DataManager.static_write(json_content)


def export():

    decrypted_content = DataManager.get_db()

    with open(f"{ARGS.data[0]}/enigma_passwords.json", "w") as out:
        json_dumps(decrypted_content, out)

def _entry_range(scope: range) -> int:
    """ checks if given range is inside the expected scope """

    print()
    entry = scope[0] - 1
    while entry not in scope:
        try:
            entry = int(input("Entry: ")) - 1
        except ValueError:
            print("Insert a number from {} to {}"
                  .format(scope[0] + 1,
                          scope[-1] + 1))
            continue

    return entry


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
    # Silences the exception output when user sends a SIGINT, typically through ^C
