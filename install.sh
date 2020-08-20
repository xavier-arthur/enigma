#!/bin/sh

git clone https://github.com/xavier-arthur/enigma /tmp/enigma
pip3 install pyinstaller
pyinstaller -n enigma --onefile /tmp/main.py
sudo mv /tmp/enigma/dist/enigma /usr/bin
echo "done!"
