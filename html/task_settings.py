#!/usr/bin/python

import cgi
import cgitb; cgitb.enable()
from spells import spells
from time import sleep
import pprint as pp
import os


print "Content-type: text/html"
print

print """
<html>
<head><title>Spell Settings</title>
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

<body>
<h3>Spell Settings</h3>
"""

form = cgi.FieldStorage()

if form.getvalue('subbut',"default") != "default":
    for idx in range(0,len(allspells.tasks)):
        #save the former config, then reload it
        cb = form.getvalue('%d_cb' %idx)
        #name = form.getvalue('%d_name' %idx)
        type = form.getvalue('%d_type' %idx)
        action = form.getvalue('%d_action' %idx)
        variable0 = form.getvalue('%d_variable0' %idx)
        allspells.tasks[idx]['enable'] = (cb == 'on')
        allspells.tasks[idx]['type'] = type
        allspells.tasks[idx]['action'] = action
        allspells.tasks[idx]['variable0'] = variable0
    allspells.saveXML('tasks.xml')
    print "Spells have been updated<br>"
    os.system('sudo pkill MagicWand')

print """
<form method="post" action="task_settings.py">
<table>
"""

for idx in range(0,len(allspells.tasks)):
    curspell = allspells.tasks[idx]
    print "<tr><td>"
    if curspell['enable']:
        checkstr = ' checked="checked"'
    else:
        checkstr = ''
    print '<input type="checkbox" name="%d_cb"%s>' %(idx,checkstr)
    print '</td><td>%s</td>' %curspell['name']

    # this is the type select box
    type = -1
    print '<td><select id="%d_type" name="%d_type" onchange="typeChange(%d)">' %(idx,idx,idx)
    for idx2 in range(0,len(allspells.types)):
        if allspells.types[idx2] == curspell['type']:
            selectedstr = ' selected="selected"'
            type = idx2
        else:
            selectedstr = ''
        print '<option value="%s"%s>%s</option>' %(allspells.types[idx2],selectedstr,allspells.types[idx2])
    
    # this is the action select box
    print '<td><div id="%d_action_div"><select id="%d_action" name="%d_action">' %(idx,idx,idx)
    for idx2 in range(0,len(allspells.actions[type])):
        if allspells.actions[type][idx2] == curspell['action']:
            selectedstr = ' selected="selected"'
        else:
            selectedstr = ''
        print '<option value="%s"%s>%s</option>' %(allspells.actions[type][idx2],selectedstr,allspells.actions[type][idx2])
    print '</select><div></td>'

    # this is the variable field
    if len(allspells.variables[type]) > 0:
        print '<td><div id="%d_variable_div"><select id="%d_variable0" name="%d_variable0">' %(idx,idx,idx)
        for idx2 in range(0,len(allspells.variables[type])):
            if allspells.variables[type][idx2] == curspell['variable0']:
                selectedstr = ' selected="selected"'
            else:
                selectedstr = ''
            print '<option value="%s"%s>%s</option>' %(allspells.variables[type][idx2],selectedstr,allspells.variables[type][idx2])
        print '</select><div></td>'
    else:
        print '<td><div id="%d_variable_div"><input type="text" id="%d_variable0" name="%d_variable0" value="%s"></div></td></tr>' %(idx,idx,idx,curspell['variable0'])

print """
</table>
<input name="subbut" type="submit">
</form>

</body>
</html>

    """
