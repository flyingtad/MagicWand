Download the latest Rasbian Lite

Flash Rasbian lite image to sd card

Boot Raspberry PI

Setup wireless network

sudo raspi-config
	hostname modify hostname and pi's password
	wifi, modify wpa_supplicant.conf
	ssh interfacing options

update apt-get
	sudo apt-get update

install git
	sudo apt-get install git

install arp-scan
	sudo apt-get install arp-scan

install pip
	wget https://bootstrap.pypa.io/get-pip.py
        sudo python get-pip.py

install apache2
	sudo apt-get install apache2

clone magicwand repo
	git clone https://github.com/flyingtad/MagicWand.git

Install Python dependencies
	sudo apt-get install python-numpy python-matplotlib python-setuptools python-dev
        sudo pip install ouimeaux
        sudo pip install picamera
        sudo pip install enum

Setup apache2
	cp misc/apache2.conf /etc/apache2/
        cd /etc/apache2/mods-enabled
        sudo ln -s ../mods-available/cgid.load
        sudo ln -s ../mods-available/cgid.conf
        cd /var
        sudo chmod 777 www
        cd www
        sudo rm -r html
        ln -s /home/pi/MagicWand/html/ html
	Modify /etc/sudoers to include:
		www-data ALL=(ALL:ALL) NOPASSWD:ALL
        sudo service apache2 reload

SOUND:
	sudo apt-get install espeak
        sudo apt-get install sox libsox-fmt-all
        wget -O - install.raspiaudio.com | bash

ACCESS POINT STUFF:
	sudo apt-get install hostapd
        sudo apt-get install dnsmasq
	cp misc/hostapd.conf /etc/hostapd/hostapd.conf
        cp misc/interfaces_* /etc/network/
        rm -f /etc/network/interfaces

SETUP SERVICE STUFF
        cp misc/magicwand /etc/init.d/
	daemon reload

Install RADIO station stuff
	sudo apt-get install mplayer

