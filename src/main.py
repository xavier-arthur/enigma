#!/usr/bin/env python3
""" main method and some auxiliars functions"""

from os.path import exists as file_exists
from getpass import getpass
from sys import exit as sys_exit
import argparse as ap
import re

from pyperclip import copy

from encrypter import Password
from login_handler import DataManager

def get_args():
    """ returns parsed args """

    args = ap.ArgumentParser(description="Command line password mananger")

    args.add_argument("--configure", action="store_true",
                      help="sets up password and other tweaks")

    args.add_argument("action", default="list", nargs="?",
                      choices=["get", "add", "remove", "list", "import"])

    args.add_argument("data", type=str, nargs="*",
                      help="takes two positional arguments in order: provider"
                      + " and username")

    args.add_argument("-y", "--auto-confirm", action="store_true",
                      help="don't ask for confirmation")

    args.add_argument("-c", "--copy", action="store_true",
                      help="sends password output to clipboard")

    args.add_argument("-m", "--manual-password", action="store_true",
                      default=None,
                      help="don't generate a password automatically")

    parsed = args.parse_args()

    if parsed.manual_password:
        parsed.manual_password = getpass("new password for {}:"
                                         .format(parsed.data[0]))

    return parsed

def main():
    """
    checks which args where given and
    directs to execution to the rigth functions
    """

    args = get_args()

    if args.configure:
        Password.configure()
        sys_exit(0)
    if not file_exists(f"{Password.config_folder}/.enigma"):
        print("config file doesn't exist did you mean to --configure?")
        sys_exit(1)
    elif not Password.check_against(getpass("enter yout password:")):
        print("invalid")
        sys_exit(2)

    if args.action == "get":
        content = get(args.data[0])
    elif args.action == "add":
        content = add(args.data[1],
                      args.data[0],
                      auto_confirm=args.auto_confirm,
                      password=args.manual_password)
        sys_exit(0)
    elif args.action == "list":
        data = DataManager.get_db()
        for i in data.keys():
            print("{} \tat {}".format(i, data[i][0]))
        sys_exit(0)
    elif args.action == "import":
        parse_csv(args.data[0])
        sys_exit(0)
    else: #remove"
        remove(args.data[0], args.auto_confirm)
        sys_exit(0)

    if args.copy:
        copy(content[1])
    else:
        print("Username:{}\nPassword:{}".format(content[0], content[1]))


def remove(provider, auto_confirm=False):
    """ deletes give login,provider,passowrd from DB """

    try:
        if not auto_confirm:
            data = get(provider)
            if input(f"delete user {data[0]} at {provider}? [y/*] ") != "y":
                sys_exit(55)

        DataManager.remove_from_db(provider)
    except KeyError:
        print(f"provider {provider} not found")


def get(provider) -> list:
    """  decodes and returns a list with user and password in this order """

    data_dict = DataManager.get_db()

    matches = re.findall(f"{provider}-?[0-9]?", str(data_dict.keys()))

    if len(matches) > 1:
        print(f"{len(matches)} entries found\n")
        for i, obj in enumerate(matches):
            print(f"{i + 1} -> {obj} at " + "{}".format(data_dict[obj][0]))

        entry = entry_range(range(len(matches)))

    try:
        return list(data_dict[provider])
    except KeyError:
        print("provider not found, was it spelled right?")
        sys_exit(1)


def add(username, provider, password=None, auto_confirm=False) -> list:
    """ adds a new user with given password to DB """

    new_password = DataManager(username, provider)
    if password:
        new_password.pwrd = password

    if auto_confirm:
        info = "y"
    else:
        info = input(f"user {new_password.info[provider][0]}"
                     + f" for provider {provider} created"
                     + " add to library? [y/*] ")

    return new_password.write_to_file() if info == "y" else sys_exit(0)

def parse_csv(filepath):

    csv_content = DataManager.import_csv(filepath)

    if file_exists(DataManager._folder_path):
        csv_content.update(DataManager.get_db())

    DataManager.static_write(csv_content)


def entry_range(scope: range) -> int:
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
    main()
