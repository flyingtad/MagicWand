#!/usr/bin/python

import cgi
import cgitb; cgitb.enable()
from xml.dom.minidom import parse
import os

filename = "/var/www/html/camera.xml"

def cameraSettings():
    camConfig = parse(filename)
    allSettings = camConfig.getElementsByTagName('camera')
    allvalues = {'na':''}
    for curSetting in allSettings[0].childNodes:
        if curSetting.nodeName.startswith('#'):
            pass
        else:
            nodeValue = curSetting.childNodes[0].nodeValue
            #print nodeValue
    
            allvalues[curSetting.nodeName]=nodeValue
    
    return allvalues

def castSettings(x):
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

def writePrevvalues(prevalues):
    f = open(filename,'w')
    f.write('<camera>\r')
    for i in prevalues.keys():
        f.write('    <%s>%s</%s>\r' %(i,prevalues[i],i))
    f.write('</camera>\r')
    f.close()

print "Content-type: text/html"
print

print """
<html>
<head><title>Sample</title></head>

<script>
function refresh(node)
{
   var times = 5000; // gap in Milli Seconds;

   (function startRefresh()
   {
      var address;
      if(node.src.indexOf('?')>-1)
       address = node.src.split('?')[0];
      else 
       address = node.src;
      node.src = address+"?time="+new Date().getTime();

      setTimeout(startRefresh,times);
   })();

}

window.onload = function()
{
  var node = document.getElementById('img');
  refresh(node);
  // you can refresh as many images you want just repeat above steps
}
</script>

<body>
<h3>Camera Settings</h3>
"""

form = cgi.FieldStorage()
if form.getvalue('subbut',"default") != "default":
    print "Settings saved, restarting wand!<br>"
    os.system('sudo pkill HarryPotterWand')

print """
<img id="img" src="image.jpg">
"""
cs = cameraSettings()
prevvalues = {'brightness':'',
          'contrast':'',
          'hflip':'',
          'resolution':'',
          'crop':'',
          'framerate':''}
#cs=prevvalues

for ckey in prevvalues.keys():
    prevvalues[ckey] = form.getvalue(ckey,cs[ckey])

writePrevvalues(prevvalues)

print """
<form method="post" action="camera.py">
"""
for ckey in prevvalues.keys():
    print """
    <p>%s: <input type="text" name="%s" value="%s"/></p>
    """ %(cgi.escape(ckey),cgi.escape(ckey),cgi.escape(prevvalues[ckey]))

print """
    <input name="subbut" type="submit">
    </form>

    </body>

    </html>

"""
