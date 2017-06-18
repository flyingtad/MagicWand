import os
from xml.dom.minidom import parse

class spells():
    def __init__(self):
        #do the config stuff here
        allConfig = parse('/var/www/html/tasks.xml')
        allTasks = allConfig.getElementsByTagName('task')
        self.tasks = []
        self.types = ['sound','say','tplinkplug','tplinkbulb','wemo']
        self.actions = [['play'],['espeak'],['toggle','on','off'],['toggle','on','off','+brightness','-brightness'],['toggle','on','off']]

        self.variables = []

        self.buildVariables()

        for curTask in allTasks:
            allvalues = {'na':''}
            for curSetting in curTask.childNodes:
                if curSetting.nodeName.startswith('#'):
                    pass
                else:
                    allvalues[curSetting.nodeName]=self.castSettings(curSetting.childNodes[0].nodeValue)
            self.tasks.append(allvalues)

    def buildVariables(self):
        for t in self.types:
            if t == 'sound':
                filename = 'sounds.txt'
                self.variables.append(self.readFile(filename))
            elif t == 'tplinkbulb':
                filename = 'tplink.txt'
                self.variables.append(self.readFile(filename))
            elif t == 'tplinkplug':
                filename = 'tplink.txt'
                self.variables.append(self.readFile(filename))
            elif t == 'wemo':
                filename = 'wemoswitches.txt'
                self.variables.append(self.readFile(filename))
            else:
                self.variables.append([])

    def readFile(self,filename):
        f = open(filename)
        x = f.read().split('\n')
        y = []
        for i in x:
            if len(i) > 0:
                y.append(i)
        return y

    def saveXML(self,filename):
        f = open(filename,'w')
        f.write('<tasks>\r')
        for t in self.tasks:
            f.write('    <task>\r')
            for i in t.keys():
                if i == 'na':
                    pass
                else:
                    f.write('    <%s>%s</%s>\r' %(i,t[i],i))
            f.write('    </task>\r')
        f.write('</tasks>\r')
        f.close()

    def castSettings(self,x):
        outx = x
        try:
            outx = float(x)
            if abs(outx-int(outx)) < .01:
                outx = int(outx)
        except:
            pass
        if x == 'True':
            outx = True
        elif x == 'False':
            outx = False
        return outx
