import os
from xml.dom.minidom import parse

def capwords(w):
    x=[0,w.find(' ')+1]
    nw = list(w)
    for xi in x:
        nw[xi]=w[xi].upper()
    return "".join(nw)

class spells():
    def __init__(self):
        #do the config stuff here
        allConfig = parse('/var/www/html/tasks.xml')
        allTasks = allConfig.getElementsByTagName('task')
        self.tasks = []
        self.types = ['sound','say','tplinkplug','tplinkbulb','wemo','radio']
        self.actions = [['play'],['espeak'],['toggle','on','off','off1on'],['toggle','on','off','+brightness','-brightness'],['toggle','on','off'],['play','stop','--','-','pause','+','++','+volume','-volume']]

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

    def duplicateSpell(self,idx):
        self.tasks.insert(idx,self.tasks[idx])

    def removeSpell(self,idx):
        self.tasks.pop(idx)

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
            elif t == 'radio':
                filename = 'radiostations.txt'
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
        f.write('<tasks>\n')
        for t in self.tasks:
            f.write('    <task>\n')
            for i in t.keys():
                if i == 'na':
                    pass
                else:
                    f.write('    <%s>%s</%s>\n' %(i,t[i],i))
            f.write('    </task>\n')
        f.write('</tasks>\n')
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

