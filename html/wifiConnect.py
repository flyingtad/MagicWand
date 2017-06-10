import os

class wifi():
    def __init__(self):
        self.ssid = ''
        self.wpa = 0
        self.psk = ''
        self.wep = False
        self.key_mgmt = ''

class wifilist():
    def __init__(self):
        out = os.popen("sudo iwlist wlan0 scanning | sed 's/^ *//'").read()
        outArray = out.split('\n')
        idx = -1
        self.wlist = []
        self.wlist.append(wifi())

        for line in outArray:
            if line.startswith('Cell'):
                if idx < 0:
                    pass
                else:
                    self.wlist.append(wifi())
                idx += 1
            elif idx < 0:
                pass
            elif line.startswith('Encryption key'):
                if line.split(":")[1].startswith('on'):
                    self.wlist[idx].wep = True
            elif line.startswith('ESSID'):
                self.wlist[idx].ssid = line.split(":")[1]
            elif line.startswith('IE: IEEE 802.11i/WPA2'):
                self.wlist[idx].wpa = 2
            elif line.startswith('IE: IEEE 802.11i/WPA'):
                self.wlist[idx].wpa = 1
            

    def disp(self,idx):
        print "---- %d ----" %idx
        print "SSID: %s" %self.wlist[idx].ssid
        print "WPA: %d" %self.wlist[idx].wpa
        print "WEP: %s" %self.wlist[idx].wep

    def displayall(self):
        for i in range(0,len(self.wlist)):
            self.disp(i)
            print " "
            self.dispwpaconf(i)
 
    def dispwpaconf(self,idx,password='password'):
        print """
network={
      ssid=%s """ %self.wlist[idx].ssid
        if self.wlist[idx].wpa:
            print "      key_mgmt=WPA-PSK"
            print '      psk="%s"' %password
        else:
            print "      key_mgmt=NONE"
            if password == '':
                pass
            else:
                print "      wep_key0=%s" %password
        print "}"

    def justnames(self):
        namelist = []
        for i in range(0,len(self.wlist)):
            namelist.append(self.wlist[i].ssid[1:-1])
        return namelist


    def appendwpaconf(self,idx,filename='/var/www/html/wpa_supplicant.conf',password='password'):
        os.popen('sudo echo " " | sudo tee --append %s' %filename).read()
        os.popen('sudo echo "network={" | sudo tee --append %s' %filename).read()
        os.popen('sudo echo \'      ssid="%s"\' | sudo tee --append %s' %(self.wlist[idx].ssid[1:-1],filename))
        if self.wlist[idx].wpa:
            os.popen('sudo echo "      key_mgmt=WPA-PSK" | sudo tee --append %s' %filename)
            os.popen('sudo echo \'      psk="%s"\' | sudo tee --append %s' %(password,filename))
        else:
            os.popen('sudo echo "      key_mgmt=NONE" | sudo tee --append %s' %filename)
            if password == "":
                pass
            else:
                os.popen('sudo echo "      wep_key0=%s" | sudo tee --append %s' %(password,filename))
        os.popen('sudo echo "}" | sudo tee --append %s' %filename)
