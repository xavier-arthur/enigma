#!/bin/sh

set -e

git clone https://github.com/xavier-arthur/enigma /tmp/enigma
pip3 install pyinstaller
pip3 install pandas
pip3 install bcrypt
pip3 install pyperclip
cd /tmp/enigma
pyinstaller -n enigma --onefile /tmp/enigma/src/main.py
sudo mv /tmp/enigma/dist/enigma /usr/bin
echo "done!"
