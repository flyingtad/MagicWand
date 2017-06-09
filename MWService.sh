#!/bin/bash

#Update acceptable devices file
sudo arp-scan -l | grep "50:c7:bf" | awk '{print $1}' > /var/www/html/tplink.txt
sudo python writewemos.py
find /home/pi/MagicWand/Sounds/* | sed 's/.*Sounds\///' > /var/www/html/sounds.txt

#Force interfaces to originals
sudo ifdown wlan0
sudo ln -f -s /etc/network/interfaces_orig /etc/network/interfaces
sudo ln -f -s /etc/dhcpcd_orig.conf /etc/dhcpcd.conf
sudo ifup wlan0
sudo service dhcpcd restart

#Give the system time to connect to the wifi before making a decision about anything
sleep 45

#run a test to see if you are connected
DEVICE='wlan0'
WLANIP=`ifconfig $DEVICE | grep 'inet addr' | sed 's/^.*inet addr://' | sed 's/ *Bcast.*/ /'`
if [[ "$WLANIP" = "" ]] ; then
    echo "Not connected, start AP"
    sudo ifdown wlan0
    sudo ln -f -s /etc/network/interfaces_ap /etc/network/interfaces
    sudo ln -f -s /etc/dhcpcd_orig.conf /etc/dhcpcd.conf
    sudo service dhcpcd restart
    sudo ifup wlan0
    sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf &
    sudo /usr/sbin/dnsmasq &
else

 while true; do

   MAGWAND=`ps aux | grep MagicWand | grep -v grep | sed 's/.*Magic/Magic/'`

   if [ "$MAGWAND" =  "MagicWand.py" ] ; then
      sleep 15
   else
      ./MagicWand.py &
      sleep 15
   fi
    

 done
fi

