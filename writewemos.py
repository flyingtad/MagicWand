import controlDevices as cd

ac = cd.autoControl()

f = open('/var/www/html/wemoswitches.txt','w')
f.write('')
for i in ac.switches:
    f.write('%s\n' %i)
f.close()
