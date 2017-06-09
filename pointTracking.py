import math
import numpy as np
from pylab import *
from time import sleep
from matplotlib import pyplot
import pprint
import controlDevices
import spells
import logging
import datetime


datestr = "{:%Y_%m_%d-%H%M%S}".format(datetime.datetime.now())
logging.basicConfig(filename='/home/pi/MagicWand/log/%s.log' %datestr, level=logging.INFO)

class getCoords():
    def __init__(self):
        self.init = True
        self.x = []
        self.y = []
        self.curt = 0
        self.t = []
        self.curidx = 0

    def wandMethod(self):
        self.x = np.zeros(15000)
        self.y = np.zeros(15000)
        self.t = np.zeros(15000)
        self.value = np.zeros(15000)
        self.curidx = 0

    def addWandPoint(self,x,y,t,val):
        self.x[self.curidx] = x
        self.y[self.curidx] = y
        self.t[self.curidx] = t
        self.value[self.curidx] = val
        self.curidx += 1

    def savePoints(self,filename):
        xstr = 'x = ' + pprint.pformat(self.x[0:self.curidx]) + '\n'
        ystr = 'y = ' + pprint.pformat(self.y[0:self.curidx]) + '\n'
        tstr = 't = ' + pprint.pformat(self.t[0:self.curidx]) + '\n'
        valstr = 'value = ' + pprint.pformat(self.value[0:self.curidx]) + '\n'

        xstr = xstr.replace('array','')
        ystr = ystr.replace('array','')
        tstr = tstr.replace('array','')
        valstr = valstr.replace('array','')

        tfile = open(filename, "w")
        tfile.write(xstr)
        tfile.write(ystr)
        tfile.write(tstr)
        tfile.write(valstr)
        tfile.close()
        
    def plotMethod(self):
        plot()
        xlim((0,100))
        ylim((100,0))
        connect('button_press_event',self.on_click)
        show(block=True)
        draw()
        self.curt = 0         

    def on_click(self,event):
        if event.button == 1:
            if event.inaxes is not None:
                #print event.xdata
                #print event.ydata
                self.x.append(event.xdata)
                self.y.append(event.ydata)
                self.t.append(self.curt)
                self.curt += .01
                clf()
                plot(self.x,self.y)
                xlim((0,100))
                ylim((100,0))
                draw()
        else:
            close("all")

class pointTracker():
    def __init__(self,window=None):
        #used for debugging
        self.shouldWait = False
        self.shouldShowLast = False
        self.win = window
        self.ac = controlDevices.autoControl()

        #buffer size
        self.arraySize = 1000

        #buffer index
        self.arrayIdx = 0
        self.breakStart = 0
        self.gestStart = 0
        self.lastDetect = 0

        #circular buffers to hold recorded info
        self.x = np.zeros(self.arraySize)
        self.y = np.zeros(self.arraySize)
        self.t = np.zeros(self.arraySize)

        #hold some additional tracking information
        self.d = np.zeros(self.arraySize) #this is the distance to previous point
        self.a = np.zeros(self.arraySize) #this is the angle from the previous
        self.dsum = np.zeros(self.arraySize) #this is the cumulative distance

        #first derivatives
        self.xdiff = np.zeros(self.arraySize)

        #an array of arrays.  this holds the gestures
        self.gestArray = []
        self.gestFeats = []
        self.gestFeatAppendNext = True
        self.buildGestures()

        self.dReference = 0
        self.dReferenceTemp = 0
        self.aReference = 0

        self.featThresh = -1 #30
        self.dThresh = -1
        self.aThresh = -1
        self.tThresh = -1
        self.intensityThresh = -1

        self.featThresh = 30 #30
        self.dThresh = 3
        self.aThresh = 65
        self.tThresh = .6
        self.intensityThresh = 20

        

    def addPt(self,x,y,t,val=255):
        if val < self.intensityThresh:
            return
        if self.arrayIdx >= self.arraySize:
            self.arrayIdx = 0
            #print "wrapping around array"
            
        prevIdx = (self.arrayIdx-1)%self.arraySize
        self.prevIdx = prevIdx
        self.x[self.arrayIdx] = x
        self.y[self.arrayIdx] = y
        self.t[self.arrayIdx] = t

        xdel = self.x[self.arrayIdx]-self.x[prevIdx]
        ydel = self.y[self.arrayIdx]-self.y[prevIdx]
        tdel = self.t[self.arrayIdx]-self.t[prevIdx]
        self.d[self.arrayIdx] = math.sqrt(xdel**2+ydel**2)
        self.a[self.arrayIdx] = math.atan2(xdel,ydel)*180/math.pi
        self.dsum[self.arrayIdx] = self.d[self.arrayIdx]+self.dsum[prevIdx]

        if tdel > self.tThresh:
            #the time has expired on the most recent gesture, close previous gesture
            #and establish this as a new gesture
            prevBounds = (self.breakStart,prevIdx)
            
            #time has expired, flush the gesture array and initialize the next one
            self.gestArray = []
            self.gestFeats = []
            self.breakStart = self.arrayIdx
            self.gestStart = self.arrayIdx
            self.dReference = self.dsum[self.arrayIdx]
            self.dReferenceTemp = self.dsum[self.arrayIdx]
            self.aReference = self.a[self.arrayIdx]
            self.gestFeatAppendNext=True

        else:
          forcePass = True
          while forcePass:
            forcePass = False

            #gesture is happening now
            subgestlen = (self.arrayIdx - self.gestStart)
            if subgestlen == 0:
                #print "this is first point on subgesture, dont try to classify"
                self.arrayIdx += 1
                return
            if subgestlen == 1:
                #print "This is the minimum vector we can process, set it up"
                #force the first angle to be same as second (no difference)
                self.dReference = self.dsum[prevIdx]
                self.aReference = self.a[self.arrayIdx]
                self.a[prevIdx] = self.a[self.arrayIdx]

            #check that enough distance has been covered for angle comparisons
            resultD = self.dsum[self.arrayIdx] - self.dReferenceTemp
            #print "(%d)-(%d)" %(self.a[self.arrayIdx],self.aReference)
            resultAt = self.a[self.arrayIdx]-self.aReference
            resultA = min(np.abs((resultAt-360,resultAt,resultAt+360)))

            if resultD > self.dThresh:
                #print "d criteria ok"
                dcrit = True
                self.dReferenceTemp = self.dsum[self.arrayIdx]
                self.aReference = self.a[self.arrayIdx]
            else:
                dcrit = False
 
            #print "current angle: %d, delta: %d" %(self.a[self.arrayIdx],resultA)
            if np.abs(resultA) > self.aThresh:
                if dcrit:
                    #print "breaking subgesture"
                    #angle has changed and distance criteria is met
                    #gesture is finished.  store it and reinitialize paramaters
                    #self.gestArray.append((self.gestStart,prevIdx,self.dsum[prevIdx] - self.dReference))
                    
                    gestLen = self.dsum[prevIdx] - self.dsum[self.gestStart]
                    #print "Gesture Length: %d\r" %gestLen
                    #self.maybeWait()

                    curfeats = self.processGesture((self.gestStart,prevIdx),(self.breakStart,prevIdx))
                    self.processFeatures(curfeats)
                    self.gestFeatAppendNext = True

                    forcePass = True
                    self.gestStart = prevIdx

                else:
                    #print "skipping D"
                    pass

            if self.dsum[self.arrayIdx] - self.dsum[self.gestStart] > 20:
                curfeats = self.processGesture((self.gestStart,self.arrayIdx),(self.breakStart,self.arrayIdx))
                self.processFeatures(curfeats)

        #increment to the next idx
        self.arrayIdx += 1

    def plot(self,x,y):
        clf()
        plot(x,y)
        yl = ylim()
        ylim(yl[::-1])
        show()
        draw()

    def processFeatures(self, feats):
        [curgests,gestdist] = self.getGestures(feats)
        #curgests = self.getGestures(feats)
        forceClear = False
        if self.gestFeatAppendNext:
            if len(self.gestFeats)-1 >= 0:
                if self.gestFeats[len(self.gestFeats)-1][0] == -1:
                    #print 'reset 1'
                    self.gestFeats = []
            self.gestFeats.append([curgests,gestdist])
        else:
            assigned = False
            if len(self.gestFeats)-2 >= 0:
                if self.gestFeats[len(self.gestFeats)-2][0] == -1:
                    #print 'reset 2'
                    self.gestFeats = []
                    self.gestFeats.append([curgests,gestdist])
                    assigned = True
            if not assigned:
                self.gestFeats[len(self.gestFeats)-1]=[curgests,gestdist]

        self.gestFeatAppendNext = False

        if forceClear:
            print 'append next 2'
            self.gestFeatAppendNext = True

        #print self.gestFeats
        #sleep(.2)
        if curgests>=0:
            #print "found %d" %curgests
            spellFound,spellName = self.matchSearch()
            if spellFound:
                #print "\rGesture Length: %d\r" %(self.dsum[self.arrayIdx] - self.dsum[self.gestStart])
                #print "=====================================\r"
                #print "SPELL FOUND: %s !!!!!!!\r" %spellName
                #print "=====================================\r\r"
                logging.info('%s was found::' %spellName)
                for gg in self.gestFeats:
                    logging.info('gesture = %d, length = %d' %(gg[0],gg[1]))
                self.doSpell(spellName)
                
                self.showLast()
                self.maybeWait()
                self.lastDetect = self.arrayIdx
                #sleep(.2)
                
                self.gestArray = []
                self.gestFeats = []
                #self.arrayIdx = 0
                self.breakStart = self.arrayIdx
                self.gestStart = self.arrayIdx
                self.dReference = self.dsum[self.arrayIdx]
                self.dReferenceTemp = self.dsum[self.arrayIdx]
                self.aReference = self.a[self.arrayIdx]
                self.gestFeatAppendNext=True

    def doSpell(self,name):
        print "==========================================\r"
        print "Spell found:  %s  !!!!!!!" %name
        print "==========================================\r"

        self.ac.doTask(name)

        """
        for checkSpell in self.allSpells:
            sname = checkSpell.getElementsByTagName('name')[0].childNodes[0].nodeValue
            #print "comparing %s to %s" %(sname,name.lower())       
            if sname == name.lower():
                print "FOUND MATCH IN XML"
                stype = checkSpell.getElementsByTagName('type')[0].childNodes[0].nodeValue
                saction = checkSpell.getElementsByTagName('action')[0].childNodes[0].nodeValue
                svariable = checkSpell.getElementsByTagName('variable0')[0].childNodes[0].nodeValue
                if stype == 'wemo':
                    if saction == 'toggle':
                        self.ac.toggleSwitch(svariable)
                    if saction == 'on':
                        self.ac.switchOn(svariable)
                    if saction == 'off':
                        self.ac.switchOff(svariable)
                elif stype.startswith('tplink'):
                    sdtype = stype[7:]
                    if sdtype == 'plug':
                        if saction == 'toggle':
                            self.ac.tpTogglePlug(svariable)
                        if saction == 'on':
                            self.ac.tpPlugOn(svariable)
                        if saction == 'off':
                            self.ac.tpPlugOff(svariable)
                    if sdtype == 'bulb':
                        if saction == 'toggle':
                            self.ac.tpToggleBulb(svariable)
                        if saction == 'on':
                            self.ac.tpBulbOn(svariable)
                        if saction == 'off':
                            self.ac.tpBulbOff(svariable)
                        if saction == '+brightness':
                            self.ac.tpBulbBrightnessUp(svariable,20)
                        if saction == '-brightness':
                            self.ac.tpBulbBrightnessDown(svariable,20)
                elif stype == 'say':
                    self.ac.speak('%s' %svariable)
                elif stype == 'alexa':
                    self.ac.speak('Alexa, %s' %svariable)
                elif stype == 'sound':
                    self.ac.playSound(svariable)
                else:
                    self.ac.speak('%s spell has not been configured' %sname)
        """

    def matchSearch(self):
        #search spells
        spellFound = False
        spellName = ''
        for spell in self.spells:
            sparray = spell[1]
            if (len(self.gestFeats)>=len(sparray)) and spell[2]:
                #testGest = self.gestFeats[len(self.gestFeats)-len(sparray):len(self.gestFeats)-1]
                startidx =  len(self.gestFeats)-len(sparray)

                tc=0
                for i in range(0,len(sparray),1):
                    tc += abs(sparray[i]-self.gestFeats[i+startidx][0])

                #tc = np.sum(abs(np.subtract(testGest,sparray)))
                if tc==0:  #matchfound
                    spellFound = True
                    spellName = spell[0]
                    #print "spell: %s" %(spell[0])
                    #sleep(2)
        return spellFound,spellName
       
    def getGestures(self,feats):
        if feats[2] < self.featThresh:
            print "Feature Pass, %d (score: %d)\r" %(feats[1],feats[2])
            #sleep(.5)
            return feats[1],feats[0]
        else:
            print "Feature Fail, %d (score: %d)\r" %(feats[1],feats[2])
            #sleep(.5)
            return -1,-1

    def ga(self,x,A):
        if A[1]<A[0]:
            out = x[A[0]:]
            #out.extend(x[0:A[1]+1])
            out = np.append(out,x[0:A[1]+1])
        else:
            out = x[A[0]:A[1]+1]
        return out

    def fixAngle(self,x):
        offsetMat = [360,0,-360]
        offset = 0
        out = x
        for i in range(1,len(x)):
            delta1 = x[i] - (out[i-1]+(offset*360))
            noffset = np.argmin(abs(np.add(offsetMat,delta1)))-1
            offset = offset+noffset
            out[i] = x[i] - (offset*360)
        return out
            

    def processGesture(self,A,B):
        #print "idxs: %d->%d" %(A[0],A[1])
        #xcur = self.x[A[0]:A[1]+1]
        xcur = self.ga(self.x,A)
        #ycur = self.y[A[0]:A[1]+1]
        ycur = self.ga(self.y,A)
        #acur = self.a[A[0]:A[1]+1]
        acur = self.fixAngle(self.ga(self.a,A))
        #dcur = self.dsum[A[0]:A[1]+1]
        dcur = self.ga(self.dsum,A)
        #xmove = self.x[B[0]:B[1]+1]
        #ymove = self.y[B[0]:B[1]+1]
        #print self.gestArray
        #processGesture(xcur,ycur,xmove,ymove)
        #print acur
        #self.plot(xcur,ycur)
        #self.plot(dcur,acur)
        gi,val = self.angleDiffs(A[0],A[1])
        #gi,val = self.angleDiffs(A[0],A[1])
        return round(self.dsum[A[1]] - self.dsum[A[0]]),gi,val

    def angleDiffs(self,sp,ep):
        if sp>ep:
            #wrap has occurred, need to behave differently
            #print [sp,ep]
            nep = ep+self.arraySize
            if (nep-sp)==1:
                dsumtemp = np.array((0,self.dsum[ep]))
                atemp = np.array((self.a[ep],self.a[ep]))
            else:
                nsp = (sp+1)%self.arraySize
                #dsumtemp = self.dsum[sp+1:ep+1]
                dsumtemp = self.ga(self.dsum,[nsp,ep])
                #atemp = self.a[sp+1:ep+1]
                atemp = self.ga(self.a,[nsp,ep])
                #print "outputs"
                #print sp,ep,nsp,nep
                #print dsumtemp
                #print atemp
        else:

            if (ep-sp)==1:
                dsumtemp = np.array((0,self.dsum[ep]))
                atemp = np.array((self.a[ep],self.a[ep]))

            else:
                #dsumtemp = self.dsum[sp+1:ep+1]
                dsumtemp = self.ga(self.dsum,[sp+1,ep])
                #atemp = self.a[sp+1:ep+1]
                atemp = self.ga(self.a,[sp+1,ep])

        if len(atemp)<2 or len(dsumtemp)<2:
            print "something is wrong"
            gi = -1
            val = 1000
        else:
            try:
                anorm,dnorm = self.normalizeVector(atemp,dsumtemp)
                gi,val = self.testGesture(anorm)
            except:
                gi = -1
                val = 1000
                print atemp
                print dsumtemp
                raise ValueError('A very specific bad thing happened')
            """
            if len(dsumtemp)<2:
                gi = -1
                val = 1000
            else:
                
                anorm,dnorm = self.normalizeVector(atemp,dsumtemp)
                gi,val = self.testGesture(anorm)
            """
        return gi,val

    def testGesture(self,x):
        idx = 0
        minidx = 0
        curmin = 500
        for ga in self.gestureProfile:
            if idx in self.validGestures:
                tempval1 = np.mean(abs(np.subtract(x-360,ga)))
                tempval2 = np.mean(abs(np.subtract(x,ga)))
                tempval3 = np.mean(abs(np.subtract(x+360,ga)))
                tempval = min([tempval1,tempval2,tempval3])
                if tempval<curmin:
                    minidx = idx
                    curmin = tempval
            idx += 1
        return minidx,curmin

    def normalizeVector(self,x,d):
        #try:
        newx = np.zeros(100)
        tempd = (d-d[0])/(d[len(d)-1]-d[0])*99
        newd = range(0,100,1)

        lastd = 0
        newx[0] = x[0]
        for i in newd[1:len(newd)-1]:
            placedi = False
            while not placedi:
                if i < tempd[lastd]:
                    pct = (i-tempd[lastd-1])/(tempd[lastd]-tempd[lastd-1])
                    newx[i] = pct*(x[lastd]-x[lastd-1])+x[lastd-1]
                    placedi = True
                else:
                    lastd += 1
        newx[99]=x[len(x)-1]
        return newx,newd
        #except:
        #print "This was an error"
        #print d

    def playback(self,x,y,t,val,valT=70):
        x = np.array(x)/208.0*100
        y = np.array(y)/208.0*100
        for i in range(0,len(x),1):
            if val[i] > valT:
                self.addPt(x[i],y[i],t[i])

    def maybeWait(self):
        if self.shouldWait:
            while 1:
                c = self.win.getch()
                if c != -1:
                    break
                sleep(.1)

    def showLast(self):
        if self.shouldShowLast:
            #clf()
            delta = 5
            for i in range(self.lastDetect,self.arrayIdx,delta):
                clf()
                maxidx = min(self.arrayIdx,i+delta)
                #print "working"
                plot(self.x[self.lastDetect:maxidx+1],self.y[self.lastDetect:maxidx+1])
                xlim((0,100))
                ylim((100,0))
                #plot(self.x[self.lastDetect:self.arrayIdx+1],self.y[self.lastDetect:self.arrayIdx+1])
                show(block=False)
                draw()
                sleep(.01)
            print "idx: %d to %d\r" %(self.lastDetect,self.arrayIdx)

    def buildGestures(self):
        self.gestureProfile = []
        self.spells = [['Mimblewimble',[0],False],
            ['Incendio',[1,2,3],False],
            ['Arresto Momentum',[1,2,1,2],False],
            ['Wingardium Leviosa', [6,5],False],
            ['Alohomora', [7,5],False],
            ['Locomotor', [4,10,8],False],
            ['Revelio',[11,2],False],
            ['Reparo',[13],False],
            ['Tarantallegra', [6,6],False],
            ['Metelojinx', [3,15],False],
            ['Silencio', [14,5],False],
            ['Descendo',[16],False],
            ['Ascendio',[17],False],
            ['Herbivicus',[5,15],False],
            ['Specialis Revelio',[12],False]
            ]

        self.spellListConfig = spells.spelllist()
        validGestures = []
        for curspell in self.spellListConfig.spells:
            if curspell.enable:
                keepspell = curspell.name
                spidx = 0
                for testspell in self.spells:
                    if keepspell.lower() == testspell[0].lower():
                        validGestures = np.append(validGestures,testspell[1])
                        self.spells[spidx][2]=True
                        break
                    spidx += 1
        validGestures = np.sort(validGestures)
        self.validGestures = np.unique(validGestures)
        
        #infinity = 0
        x = array([-116.56505118, -110.14186594, -103.7186807 ,  -97.29549547,
        -90.87231023,  -84.50143047,  -78.13877043,  -71.77611038,
        -66.8737255 ,  -63.84706789,  -60.82041028,  -57.79375267,
        -54.76709506,  -51.74043745,  -48.33430127,  -42.21878515,
        -36.10326903,  -29.98775291,  -26.62902024,  -23.76668024,
        -20.90434025,  -18.04200025,  -15.17966026,   -9.9651262 ,
         -3.18592761,    3.59327099,   10.37246959,   17.15166819,
         24.26442504,   38.54392118,   52.82341732,   63.97451143,
         71.73044688,   79.48638233,   87.24231779,   94.99825324,
        102.25771641,  109.26734445,  116.27697248,  123.28660052,
        129.8707877 ,  133.91843929,  137.96609088,  142.01374247,
        145.37871102,  146.8032131 ,  148.22771518,  149.65221727,
        151.07671935,  151.13321465,  150.12781161,  149.12240856,
        148.11700551,  146.24486709,  143.15075973,  140.05665237,
        136.96254501,  132.82487028,  126.87726614,  120.929662  ,
        115.34066248,  109.840868  ,  104.34107352,   98.84127904,
         93.34148456,   86.99878887,   79.35111779,   71.70344671,
         65.08540679,   61.41116246,   57.73691813,   54.06267381,
         50.38842948,   46.71418515,   43.03994082,   37.54615438,
         30.19905159,   22.85194879,   15.504846  ,    8.15774321,
          0.95688267,   -6.24342561,  -13.44373389,  -20.64404216,
        -27.84435044,  -35.04465871,  -41.57207228,  -47.23481053,
        -52.89754877,  -58.56028702,  -64.22302527,  -69.21946147,
        -72.64585877,  -76.07225606,  -79.49865336,  -82.92505065,
        -86.35144795,  -89.77784525,  -94.572647  ,  -99.46232221])  
        self.gestureProfile.append(x)

        #upleft = 1
        x = 150*np.ones(100)
        self.gestureProfile.append(x)

        #downright = 2
        x = 30*np.ones(100)
        self.gestureProfile.append(x)
 
        #little bump, right to left = 3
        x,na = self.normalizeVector(np.array([-145.0,-55.0]),np.array([0.0,99.0]))
        self.gestureProfile.append(x)

        #up = 4
        x = 180*np.ones(100)
        self.gestureProfile.append(x)

        #down = 5 
        x = np.zeros(100)
        self.gestureProfile.append(x)

        #little valley, left to right = 6
        x,na = self.normalizeVector(np.array([35,145.0]),np.array([0.0,99.0]))
        self.gestureProfile.append(x)

        #cw circle = 7
        x,na = self.normalizeVector(np.array([90,-270.0]),np.array([0.0,99.0]))
        self.gestureProfile.append(x)

        #right = 8
        x = 90*np.ones(100)
        self.gestureProfile.append(x)

        #left = 9
        x = 270*np.ones(100)
        self.gestureProfile.append(x)

        #down left = 10
        x = 315*np.ones(100)
        self.gestureProfile.append(x)

        #revelio p1 = 11
        x,na = self.normalizeVector(np.array([180,180,-90]),np.array([0.0,45.0,99.0]))
        self.gestureProfile.append(x)

        #down right = 12
        """
        x =  array([-127.92721622, -110.93369918,  -95.51766559,  -65.51542688,
        -26.07548477,  -11.81203583,   20.97708507,   35.97891039,
         44.72991419,   49.29781234,   32.10376458,   -1.73882827,
        -20.62805526,  -47.84923515,  -72.01220864,  -86.3152311 ,
        -95.51766559, -110.06571461, -128.80386517, -156.29020288,
       -165.91220722, -176.68553408,  174.95803343,  170.19318703,
        146.7388057 ,  126.64267617,  106.88832938,   95.6451639 ,
         88.67669956,   78.23060607,   52.80143362,   39.70521024,
         22.69761994,    7.22003188,   -7.65697888])
        d = array([  3.67324998,   5.17032125,   4.26934698,   7.42871505,
         5.71284015,   5.6617631 ,   5.93523764,   8.87742522,
         5.48938542,  10.70136612,   7.99610781,   6.36582128,
         6.57946369,   7.03467162,   7.31118803,   6.38755282,
         6.40402047,   6.58063218,   9.17109693,   6.72529142,
        12.69715178,  13.36389796,  13.18731609,  10.20661386,
         8.10041736,   9.6295376 ,   8.47845903,   8.34644756,
         8.88782528,  10.06282107,   5.09249708,   9.07094424,
         8.00946244,  10.75854121,   5.79883157])
        x,na = self.normalizeVector(x,d)
        """
        x,na = self.normalizeVector(np.array([180,5000]),np.array([0.0,99.0]))
        self.gestureProfile.append(x)

        #reparo = 13
        x,na = self.normalizeVector(np.array([180,-270]),np.array([0,99.0]))
        self.gestureProfile.append(x)

        #little valley, right to left = 14
        x,na = self.normalizeVector(np.array([-55,-145.0]),np.array([0.0,99.0]))
        self.gestureProfile.append(x)

        #little bump, left to right = 15
        x,na = self.normalizeVector(np.array([145,35.0]),np.array([0.0,99.0]))
        self.gestureProfile.append(x)

        #descendo = 16
        x,na = self.normalizeVector(np.array([90,360,360]),np.array([0.0,60.0,99.0]))
        self.gestureProfile.append(x)

        #ascendio = 17
        x,na = self.normalizeVector(np.array([90,-180,-180]),np.array([0.0,60.0,99.0]))
        self.gestureProfile.append(x)

        

def angleDistance(x,y):
    d = np.zeros(len(x)-1)
    a = np.zeros(len(x)-1)
    for i in range(0,len(x)-1,1):
        xdel = x[i+1]-x[i]
        ydel = y[i+1]-y[i]
        d[i] = math.sqrt(xdel**2+ydel**2)
        a[i] = math.atan2(xdel,ydel)*180/math.pi
    return a,d

def stepThru(x,y,t):
    firstStep = True
    d = np.zeros(len(x)-1)
    dsum = np.zeros(len(x)-1)
    a = np.zeros(len(x)-1)
    adelta = np.zeros(len(x)-1)
    curlength = 0
    for i in range(1,len(x)-1,1):
        xdel = x[i]-x[i-1]
        ydel = y[i]-y[i-1]
        tdel = t[i]-t[i-1]
        if tdel > .6:
            print "inactive threshold, flush array"
            """
            subplot(2,1,1)
            subplot(2,2,1)
            plot(x[i-curlength:i-1],y[i-curlength:i-1])
            #show(plot(a[i-curlength:i]))
            subplot(2,2,2)
            plot(dsum[i-curlength:i-1],a[i-curlength:i-1])
            subplot(2,2,3)
            plot(dsum[i-curlength:i-1],adelta[i-curlength:i-1])
            subplot(2,2,4)
            plot(dsum[i-curlength:i])
            print "curlength: %d" %curlength
            show()
            """

            gestbreaks = [i-curlength]
            adelts = []
            relativeD = dsum[i-curlength]
            relativeDabs = dsum[i-curlength]
            relativeA = a[i-curlength]
            resultD = 0
            resultA = 0

            angleThresh = 70
            dThresh = 5
            dcrit = False

            for k in range(i-curlength+1,i,1):
                resultD = dsum[k]-relativeD
                resultAt = a[k]-relativeA
                resultA = min(np.abs((resultAt-360,resultAt,resultAt+360)))

                if resultD > dThresh:
                    dcrit = True
                    relativeD = dsum[k]
                    relativeA = a[k]
                else:
                    dcrit = False
                print "%d = %d" %(resultA,adelta[k])
                if np.abs(resultA) > angleThresh:
                    if dcrit:
                        #print "%d = %d" %(resultA,adelta[k])
                        gestbreaks.append(k)
                        adelts.append(dsum[k]-relativeDabs)
                        relativeDabs = dsum[k]
                    else:
                        print "skipping D"
                    
                    
            gestbreaks.append(i)
            adelts.append(resultD)
            print adelts
            print gestbreaks
            for k in range(0,len(gestbreaks)-1,1):
                print adelts[k]
                if adelts[k]>15:
                    xgest = x[gestbreaks[k]-1:gestbreaks[k+1]-1]
                    ygest = y[gestbreaks[k]-1:gestbreaks[k+1]-1]
                    #processGesture(xgest,ygest,x[i-curlength:i-1],y[i-curlength:i-1])

            print gestbreaks

            show()
            curlength = 0
            
        lastd = math.sqrt(xdel**2+ydel**2)
        lasta = math.atan2(ydel,xdel)*180.0/math.pi
        #print "%d,%d:::%d,%d,%d" %(x[i],y[i],xdel,ydel,lasta)

        d[i] = lastd
        a[i] = lasta
        dsum[i] = dsum[i-1]+d[i]
        adeltatemp = (a[i]-a[i-1])
        n = np.argmin(np.abs([adeltatemp-360,adeltatemp,adeltatemp+360]))
        adelta[i] = adeltatemp+360*(n-1)
        
        curlength += 1

def processGesture(x,y,xall,yall):
    clf()
    subplot(2,2,1)
    fig1 = plot(xall,yall)
    
    xl = xlim()
    yl = ylim()
    yl = yl[::-1]
    ylim(yl)
    subplot(2,2,3)
    fig2 = plot(x,y)
    xlim(xl)
    ylim(yl)
    show(block=False)
    draw()
    #sleep(.01)
