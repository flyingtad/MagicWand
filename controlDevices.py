from ouimeaux.environment import Environment
from pyHS100 import SmartBulb, SmartPlug
import os
from xml.dom.minidom import parse

class autoControl():
    def __init__(self):
        print "Setting up devices for control"
        #do the config stuff here
        self.taskConfig = parse("/var/www/html/tasks.xml")
        self.allTasks = self.taskConfig.getElementsByTagName('task')
        self.switches = []
        self.motions = []

        self.env = Environment(self.on_switch, self.on_motion)
        self.env.start()
        self.env.discover()

    def doTask(self,name):
        for checkTask in self.allTasks:
            sname = checkTask.getElementsByTagName('name')[0].childNodes[0].nodeValue
            #print "comparing %s to %s" %(sname,name.lower())
            if sname == name.lower():
                stype = checkTask.getElementsByTagName('type')[0].childNodes[0].nodeValue
                saction = checkTask.getElementsByTagName('action')[0].childNodes[0].nodeValue
                svariable = checkTask.getElementsByTagName('variable0')[0].childNodes[0].nodeValue
                print '%s: %s --- %s --- %s' %(sname,stype,saction,svariable)
                if stype == 'wemo':
                    if saction == 'toggle':
                        self.toggleSwitch(svariable)
                    if saction == 'on':
                        self.switchOn(svariable)
                    if saction == 'off':
                        self.switchOff(svariable)
                elif stype.startswith('tplink'):
                    sdtype = stype[6:]
                    if sdtype == 'plug':
                        if saction == 'toggle':
                            self.tpTogglePlug(svariable)
                        if saction == 'on':
                            self.tpPlugOn(svariable)
                        if saction == 'off':
                            self.tpPlugOff(svariable)
                    if sdtype == 'bulb':
                        if saction == 'toggle':
                            self.tpToggleBulb(svariable)
                        if saction == 'on':
                            self.tpBulbOn(svariable)
                        if saction == 'off':
                            self.tpBulbOff(svariable)
                        if saction == '+brightness':
                            self.tpBulbBrightnessUp(svariable,30)
                        if saction == '-brightness':
                            self.tpBulbBrightnessDown(svariable,30)
                elif stype == 'say':
                    self.speak('%s' %svariable)
                elif stype == 'alexa':
                    self.speak('Alexa, %s' %svariable)
                elif stype == 'sound':
                    self.playSound(svariable)
                else:
                    self.speak('%s spell has not been configured' %sname)

    def on_switch(self, switch):
        print "Switch Found: ", switch.name
        self.switches.append(switch.name)

    def on_motion(self, motion):
        print "Motion Found: ", motion.name
        self.motions.append(motion.name)

    def toggleSwitch(self,name):
        switch = self.env.get_switch(name)
        state = switch.get_state()
        if state == 0:
            switch.on()
        else:
            switch.off()

    def switchOn(self, name):
        switch = self.env.get_switch(name)
        switch.on()

    def switchOff(self, name):
        switch = self.env.get_switch(name)
        switch.off()

    def playSound(self, filename):
        os.system('play /home/pi/MagicWand/Sounds/%s &' %filename)

    def speak(self,talkstring):
        os.system('espeak "%s" -s 120 &' %talkstring)

    def tpTogglePlug(self, ip):
        plug = SmartPlug(ip)
        if plug.state == 'OFF':
            plug.state = 'ON'
        else:
            plug.state = 'OFF'
    def tpPlugOn(self,ip):
        plug = SmartPlug(ip)
        plug.turn_on()
    def tpPlugOff(self,ip):
        plug = SmartPlug(ip)
        plug.turn_off()
    def tpToggleBulb(self,ip):
        bulb = SmartBulb(ip)
        if bulb.state == 'OFF':
            bulb.state = 'ON'
        else:
            bulb.state = 'OFF'
    def tpBulbOn(self,ip):
        bulb = SmartBulb(ip)
        bulb.turn_on()
    def tpBulbOff(self,ip):
        bulb = SmartBulb(ip)
        bulb.turn_off()
    def tpBulbBrightnessUp(self,ip,delta):
        bulb = SmartBulb(ip)
        bulb.brightness += delta
    def tpBulbBrightnessDown(self,ip,delta):
        bulb = SmartBulb(ip)
        bulb.brightness -= delta
