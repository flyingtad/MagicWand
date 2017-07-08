#!/usr/bin/python

import cgi
import cgitb; cgitb.enable()
from spells import spells, capwords
from time import sleep
import pprint as pp
import os


print "Content-type: text/html"
print

print """
<html>
<head><title>Spell Settings</title>
<link rel="stylesheet" type="text/css" href="formstyle.css">
<script>
"""

allspells = spells()

print 'var atypes = %s;' %(pp.pformat(allspells.types))
print 'var aactions = %s;' %(pp.pformat(allspells.actions))
print 'var avariables = %s;' %(pp.pformat(allspells.variables))

print """

function typeChange(num){
    numstr = num.toString()

    //GET TYPE INFO
    var typeObj = document.getElementById(numstr.concat("_type"));
    var type = typeObj.options[typeObj.selectedIndex].value

    var foundidx = -1;
    for (i = 0; i < atypes.length; i++){
        if (atypes[i] == type){
            foundidx = i;
            break;
        }
    }

    //BUILD ACTION DROP DOWN
    var obj = document.getElementById(numstr.concat("_action"));
    document.getElementById(numstr.concat("_action_div")).removeChild(obj);
    
    var element = document.createElement('select');
    element.setAttribute('id',numstr.concat("_action"));
    element.setAttribute('name',numstr.concat("_action"));
    for (i = 0; i < aactions[foundidx].length; i++) { 
        var opelem = document.createElement('option');
        opelem.text = aactions[foundidx][i]
        opelem.setAttribute('value',aactions[foundidx][i])
        element.add(opelem)
    }
    document.getElementById(numstr.concat("_action_div")).appendChild(element);

    var obj2 = document.getElementById(numstr.concat("_variable0"));
    document.getElementById(numstr.concat("_variable_div")).removeChild(obj2);
    

    if ( avariables[foundidx].length > 0 ) {
        var element = document.createElement('select');
        element.setAttribute('id',numstr.concat("_variable0"));
        element.setAttribute('name',numstr.concat("_variable0"));
        for (i = 0; i < avariables[foundidx].length; i++){
            var opelem = document.createElement('option');
            opelem.text = avariables[foundidx][i]
            opelem.setAttribute('value',avariables[foundidx][i])
            element.add(opelem)
        }   
    }else {
        var element = document.createElement('input');
        element.setAttribute('id',numstr.concat("_variable0"));
        element.setAttribute('name',numstr.concat("_variable0"));
    }
    document.getElementById(numstr.concat("_variable_div")).appendChild(element);
}
</script>

</head>

<body class="form-style-3">
<div class="h2">Spell Settings</div>
<div class="spell" style="text-align:center;background-color:rgba(0,0,0,0)">I solemnly swear that I am up to no good.</div>
"""

form = cgi.FieldStorage()

subvalue = form.getvalue('subbut',"default")
addorsub = False
addidx=-1
remidx=-1
spellRemoveButton = {}
if subvalue != "default":
    if subvalue.startswith('add'):
        addorsub = True
        print "Saved, one item added"
        idxchange = int(subvalue.split('_')[1])
        addidx = idxchange
        allspells.duplicateSpell(idxchange)
    elif subvalue.startswith('del'):
        addorsub = True
        print "Saved, one item removed"
        idxchange = int(subvalue.split('_')[1])
        remidx = idxchange
        allspells.removeSpell(idxchange)
    for idx in range(0,len(allspells.tasks)):
        #save the former config, then reload it
        modidx = idx
        if addidx >= 0:
            if idx>addidx:
                modidx = idx-1
        elif remidx >= 0:
            if idx>=remidx:
                modidx = idx+1
        cb = form.getvalue('%d_cb' %modidx)
        #name = form.getvalue('%d_name' %modidx)
        type = form.getvalue('%d_type' %modidx)
        action = form.getvalue('%d_action' %modidx)
        variable0 = form.getvalue('%d_variable0' %modidx)
        #allspells.tasks[idx]['name'] = name
        allspells.tasks[idx]['enable'] = (cb == 'on')
        allspells.tasks[idx]['type'] = type
        allspells.tasks[idx]['action'] = action
        allspells.tasks[idx]['variable0'] = variable0
    allspells.saveXML('tasks.xml')
    if subvalue == 'Save':
        print "Spells have been updated<br>"
        os.system('sudo pkill MagicWand')
    elif subvalue == 'Reboot':
        os.system('sudo reboot')
    elif not addorsub:
        print "Spells saved, '%s' tested" %subvalue
        os.system('sudo -u pi echo "%s" > /tmp/tasks &' %subvalue)
        os.system('sudo chmod 777 /tmp/tasks')

for idx in range(0,len(allspells.tasks)):
    if allspells.tasks[idx]['name'] in spellRemoveButton.keys():
        spellRemoveButton[allspells.tasks[idx]['name']] = True
    else:
        spellRemoveButton[allspells.tasks[idx]['name']] = False

print """
<form method="post" action="task_settings.py">
"""

for idx in range(0,len(allspells.tasks)):
    curspell = allspells.tasks[idx]
    print '<div class="spell"><table width="100%%"><tr>'
    if curspell['enable']:
        checkstr = ' checked="checked"'
    else:
        checkstr = ''
    print '<td style="width:30px">'
    print '<input type="checkbox" name="%d_cb"%s></td>' %(idx,checkstr)

    print '<td style="width:350px">'
    print '<input name="%d_name" type="hidden" value="%s" style="border:0px;width:100%%" readonly>' %(idx,curspell['name'])
    print '<label class="titlelabel">%s</label>' %capwords(curspell['name'])
    print '</td><td>'
    print '<button name="subbut" value="add_%d" type="submit">Duplicato</button>' %(idx)
    print '</td><td>'
    if spellRemoveButton[curspell['name']]:
        print '<button name="subbut" value="del_%d" type="submit">Obliviate</button>' %(idx)
    print '</td></tr></table><table>'
    print '<tr><td style="width:100px"><label>Type:</label></td><td style="width:120px"><label>Action</label></td><td style="width:300"><label>Argument:</td><td></td></tr><tr>'

    # this is the type select box
    type = -1
    print '<td>'
    #print '<label>Type:</label>'
    print '<select style="width:100%%" id="%d_type" name="%d_type" onchange="typeChange(%d)">' %(idx,idx,idx)
    for idx2 in range(0,len(allspells.types)):
        if allspells.types[idx2] == curspell['type']:
            selectedstr = ' selected="selected"'
            type = idx2
        else:
            selectedstr = ''
        print '<option value="%s"%s>%s</option>' %(allspells.types[idx2],selectedstr,allspells.types[idx2])
    
    # this is the action select box
    print '<td>'
    #print '<label>Action:</label>'
    print '<div id="%d_action_div"><select style="width:100%%" id="%d_action" name="%d_action">' %(idx,idx,idx)
    for idx2 in range(0,len(allspells.actions[type])):
        if allspells.actions[type][idx2] == curspell['action']:
            selectedstr = ' selected="selected"'
        else:
            selectedstr = ''
        print '<option value="%s"%s>%s</option>' %(allspells.actions[type][idx2],selectedstr,allspells.actions[type][idx2])
    print '</select><div></td>'

    # this is the variable field
    print '<td>'
    #print '<label>Argument:</label>'
    if len(allspells.variables[type]) > 0:
        print '<div id="%d_variable_div"><select style="width:100%%" id="%d_variable0" name="%d_variable0">' %(idx,idx,idx)
        for idx2 in range(0,len(allspells.variables[type])):
            if allspells.variables[type][idx2] == curspell['variable0']:
                selectedstr = ' selected="selected"'
            else:
                selectedstr = ''
            print '<option value="%s"%s>%s</option>' %(allspells.variables[type][idx2],selectedstr,allspells.variables[type][idx2])
        print '</select></div></td>'
    else:
        print '<div id="%d_variable_div"><input style="display:block;width:100%%" type="text" id="%d_variable0" name="%d_variable0" value="%s"></div></td>' %(idx,idx,idx,curspell['variable0'])
    print '<td><button name="subbut" value="%s" type="submit">Test</button>' %(curspell['name'])
    print ''
    print '</td></tr>'
    print "</table></div><br>"
print """
<input name="subbut" value="Save" type="submit">
<input name="subbut" value="Reboot" type="submit">
</form>

</body>
</html>

    """
