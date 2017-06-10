#!/usr/bin/python

import cgi
import cgitb; cgitb.enable()
import wifiConnect as wc
from time import sleep
import os


print "Content-type: text/html"
print

print """
<html>
<head><title>Wifi Settings</title></head>

<body>
<h3>Wifi Settings</h3>
"""

wifi = wc.wifilist()

namelist = wifi.justnames()


##  <option value="fiat">Fiat</option>
##  <option value="audi">Audi</option>
##</select>
#
form = cgi.FieldStorage()

if form.getvalue('subbut',"default") != "default":
    for idx in range(0,len(wifi.wlist)):
        if wifi.wlist[idx].ssid[1:-1] == form.getvalue('ssid'):
            wifi.appendwpaconf(idx,'/etc/wpa_supplicant/wpa_supplicant.conf',form.getvalue('password'))
            print "Configuration Saved"
            print "</body>"
            print "</html>"
            sleep(5)
            os.system('sudo reboot')
            break
    
else:
    print """
<form onsubmit="saveConfig()" method="post" action="wifi_setup.py">
<p> <select name="ssid">
"""
    for idx in range(0,len(namelist)):
        print '<option value="%s">%s</option>' %(namelist[idx],namelist[idx])

    print """
</select>
<p> <input type="password" name="password" value=""/></p>
<input name="subbut" type="submit">
</form>

</body>
</html>

    """
