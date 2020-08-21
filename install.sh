#!/bin/sh

set -e

git clone https://github.com/xavier-arthur/enigma /tmp/enigma
pip3 install pyinstaller
cd /tmp/enigma
pyinstaller -n enigma --onefile /tmp/enigma/src/main.py
sudo mv /tmp/enigma/dist/enigma /usr/bin
echo "done!"
