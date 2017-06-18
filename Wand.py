import picamera
from picamera.array import PiRGBArray
from time import sleep
import io
import numpy as np
import time
import pointTracking as PT
from xml.dom.minidom import parse
import math

class Wand():
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.pt = PT.pointTracker()
        self.setCameraSettings()
        self.setDetectionSettings()
        self.getStill()
        #self.preview(10)

    def setDetectionSettings(self):
        config = parse("/home/pi/MagicWand/html/detection.xml")
        allSettings = config.getElementsByTagName('detection')
        for curSetting in allSettings[0].childNodes:
            if curSetting.nodeName.startswith('#'):
                pass
            else:
                nodeValue = curSetting.childNodes[0].nodeValue
                print 'Setting Detection %s to %s' %(curSetting.nodeName,nodeValue)
                curSettingVal = self.castSettings(nodeValue)
                setattr(self.pt,curSetting.nodeName,curSettingVal)

    def setCameraSettings(self):
        camConfig = parse("/home/pi/MagicWand/html/camera.xml")
        allSettings = camConfig.getElementsByTagName('camera')
        for curSetting in allSettings[0].childNodes:
            if curSetting.nodeName.startswith('#'):
                pass
            else:
                nodeValue = curSetting.childNodes[0].nodeValue
                print 'Setting Camera %s to %s' %(curSetting.nodeName,nodeValue)
                if nodeValue.find(',')>0:
                    vals = nodeValue.split(',')
                    setVals = []
                    for cv in vals:
                        setVals.append(self.castSettings(cv))
                    setattr(self.camera,curSetting.nodeName,setVals)
                else:
                    curSettingVal = self.castSettings(nodeValue)
                    setattr(self.camera,curSetting.nodeName,curSettingVal)

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

    def preview(self, duration):
        self.camera.start_preview()
        sleep(duration)
        self.camera.stop_preview()

    def getStill(self):
        self.camera.capture('/home/pi/MagicWand/html/image.jpg')

    def detectSpells(self, saveMode=False):
        XDIM = self.camera.resolution[0]
        YDIM = self.camera.resolution[1]
    
        rawCap = PiRGBArray(self.camera, size=(XDIM,YDIM))

        sleep(0.1)

        firstFrame = True

        firsttime = time.time()
        lasttime = firsttime

        for frame in self.camera.capture_continuous(rawCap, format="bgr", use_video_port=True):
            et = time.time()-lasttime
            lasttime = time.time()

            rgbnum = 2
            image = frame.array[:,:,rgbnum].astype(int)
        
            if firstFrame:
                previmage = image
                firstFrame = False

            diffimage = np.subtract(previmage,image)
            maxidx = np.argmax(diffimage)
            y = maxidx/XDIM #y
            x = maxidx%XDIM #x
            val = diffimage[y,x]


            #print val,x,y

            x = 100.0*x/XDIM
            y = 100.0*y/YDIM
            
            mytime = time.time() - firsttime
            #if val>threshold:
            
            self.pt.addPt(x,y,mytime,val)
                
            rawCap.truncate(0)

            previmage = image
            
