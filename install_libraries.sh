#!/usr/bin/env bash
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install sublime-text

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

sudo pip install beautifulsoup4
sudo pip install python-dateutil
sudo pip install pytz
sudo pip install lxml

sudo pip install xvfbwrapper
sudo apt-get install xvfb x11-xkb-utils -y