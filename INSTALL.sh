#!/bin/bash

# This install script will complete the setup for running the Magic Wand
# spell detections.  Before you run this, complete these steps:
#
#	With your latest version Rasbian Lite flashed microsd card...
#
#	1) > sudo raspi-config
#		a) modify hostname (ie magicwand)
#		b) modify /etc/wpa_supplicant/wpa_supplicant.conf
#		c) change pi's password
#               d) enable ssh
#		e) reboot
#	2) > sudo apt-get update
#	3) > sudo apt-get install git
#	4) > git clone https://github.com/flyingtad/MagicWand.git
#	5) > MagicWand/INSTALL.sh
#

# Install arp-scan
sudo apt-get install arp-scan

# Install pip
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

# Install apache2
sudo apt-get install apache2

# Install Python dependencies
sudo apt-get install python-numpy python-matplotlib python-setuptools python-dev
sudo pip install ouimeaux
sudo pip install picamera
sudo pip install enum

# Setup apache2
cd ~/MagicWand
cp misc/apache2.conf /etc/apache2/

cd /etc/apache2/mods-enabled
sudo ln -s ../mods-available/cgid.load
sudo ln -s ../mods-available/cgid.conf

cd /var
sudo chmod 777 www
cd www
sudo rm -r html
ln -s /home/pi/MagicWand/html/ html
#Modify /etc/sudoers to include:
#		www-data ALL=(ALL:ALL) NOPASSWD:ALL
sudo service apache2 reload

# Enabling the playing of sounds
sudo apt-get install espeak
sudo apt-get install sox libsox-fmt-all

# If using pizeroaudio
wget -O - install.raspiaudio.com | bash

# Setup AP
sudo apt-get install hostapd
sudo apt-get install dnsmasq
cp misc/hostapd.conf /etc/hostapd/hostapd.conf
cp misc/interfaces_* /etc/network/
rm -f /etc/network/interfaces
#NEEDS MORE WORK

#SETUP SERVICE STUFF
cd ~/MagicWand
cp misc/magicwand /etc/init.d/
#NEEDS MORE WORK

