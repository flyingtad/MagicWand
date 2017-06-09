from xml.dom.minidom import parse

class spelllist():
    def __init__(self):
        self.taskConfig = parse("/var/www/html/tasks.xml")
        self.allTasks = self.taskConfig.getElementsByTagName('task')
        self.spells = []

        for curTask in self.allTasks:
            curspell = spell()
            for curSetting in curTask.childNodes:
                if curSetting.nodeName.startswith('#'):
                    pass
                else:
                    nodeValue = self.castSettings(curSetting.childNodes[0].nodeValue)
                    setattr(curspell, curSetting.nodeName, nodeValue)
            self.spells.append(curspell)

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

        
class spell():
    def __init__(self):
        pass
            
