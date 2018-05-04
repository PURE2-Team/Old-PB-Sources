# 2013-06-15
#
#@author: stibbich <stibbich@pb-powerboard.com>
#Edited by Franc 25.05.2016 / 12.11.2016
#

Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from Screens.Screen import Screen
from Components.config import config, ConfigBoolean, ConfigClock, ConfigDateTime, getConfigListEntry
from Components.ConfigList import *
from Components.ActionMap import ActionMap, NumberActionMap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.Label import Label
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.ChoiceList import ChoiceList, ChoiceEntryComponent

from enigma import *
from Tools.Directories import fileExists, resolveFilename, SCOPE_ACTIVE_SKIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Plugins.Extensions.PowerboardCenter.PBCon import PBConsole2
from Components.Input import Input
from Components.Button import Button
import os
import gettext
import re
from time import *

from Plugins.Extensions.PowerboardCenter.PBTimeInput import PBTimeInput


#************************************************************************************************************************************** 
import sys
from Components.Sources.List import List
#************************************************************************************************************************************** 


class UserScript(Screen):
    skin = """
        <screen name="UserScript" position="center,center" size="850,420" title="PB-Script-Starter" flags="wfNoBorder">
            <widget name="menu" position="45,74" size="650,300" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PB Script Starter" position="20,8" size="485,50" font="Regular;28" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
            <widget source="global.CurrentTime" render="Label" position="755,20" size="90,28" font="Regular;23" halign="right" backgroundColor="black" foregroundColor="grey" shadowOffset="-2,-2" shadowColor="black" transparent="1">
               <convert type="ClockToText">Format:%d.%b</convert>
            </widget>
            <widget source="global.CurrentTime" render="Label" position="675,20" size="80,28" font="Regular;23" halign="right" backgroundColor="black" shadowOffset="-2,-2" shadowColor="black" transparent="1">
               <convert type="ClockToText">Default</convert>
            </widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb_small.png" position="680,200" size="150,150" backgroundColor="black" alphatest="blend" />
         </screen>"""


    def __init__(self, session, args = 0):
        self.session = session
        global userkit
        Screen.__init__(self, session)
		
		

		
        global est
        est = False
		
		
		
#************************************************************************************************************************************** 
	    # Estuary - Start Here	
        self["page"] = Label()
        self["page"].setText(" ")

        if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
            est = True
            l = []
            l.append(self.buildListEntry(_("Start script"), _("Configure how to handle script"), "syssetup.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
        else:
            est = False
            list = []
            list.append(SimpleEntry(_("Configure how to handle script"), "system.png"))  
            self['menu'] = ExtrasList(list)
			
#************************************************************************************************************************************** 
		
		
		

        
        
		
		
        self["actions"] = ActionMap(["SetupActions", "OkCancelActions", "ColorActions", "DirectionActions"],
        {
            "red": self.cancel,
            "ok": self.go,
            "cancel": self.cancel,
        }, -2)
		
		
 #************************************************************************************************************************************** 
		# Estuary - Start Here	
        #Postavi caption na color gumbe
        self["key_red"] = Button(_("Back"))

#************************************************************************************************************************************** 
		# Estuary - Start Here	
    def buildListEntry(self, title, description, image):
        pixmap = LoadPixmap(cached=True, path="%s/pics/fhd/%s" % (os.path.dirname(sys.modules[__name__].__file__), image));
        return((pixmap, title, description))	
#************************************************************************************************************************************** 




    def go(self):
        usrscriptlist = self.getUserScriptList()
        if usrscriptlist == []:
            self.session.open(MessageBox,_("There is no Script to execute"), MessageBox.TYPE_ERROR)
        else:
            os.system("chmod 755 /tmp/*.sh")
            os.system("chmod 755 /usr/script/*.sh")
            self.session.openWithCallback(self.askForUserScript,ChoiceBox,_("Select Script to execute!"),usrscriptlist)


    def askForUserScript(self, userkit):
        if userkit is None:
            self.skipUserScript(_("No Script selected"))
        else:
            self.userkit=userkit[1]
            self.session.openWithCallback(self.WhatTodo, DialogWhatTodo, _("How to execute %s?") % self.userkit, userkit)

    def WhatTodo(self, answer):
        if answer == 0:
            self.session.openWithCallback(self.UserScriptPerformever, DialogPerformever, _("How to execute the script?"))
        elif answer == 1:
            self.session.openWithCallback(self.UserScriptDelete,MessageBox,_("Remove %s from autostart?") % self.userkit,MessageBox.TYPE_YESNO)
        elif answer == 2:
            self.session.openWithCallback(self.delstart,MessageBox,_("switch off starting of script?"), MessageBox.TYPE_YESNO)

    def UserScriptPerformever(self,answer):
        print "answer:", answer
        if answer == 0:
            self.session.openWithCallback(self.UserScriptPerformstart, DialogPerformstart, _("Execute at Startup"))
        elif answer == 1:
            self.session.openWithCallback(self.UserScriptPeriodstart, DialogPeriodstart, _("Execute every day/week"))
        elif answer == 2:
            self.session.openWithCallback(self.UserScriptPerform,MessageBox,_("Execute %s ?") % self.userkit,MessageBox.TYPE_YESNO)

    def UserScriptPeriodstart(self, answer):
        print "answer:", answer
        if os.path.isfile("/etc/init.d/busybox-cron"):
            if answer == 0:
                self.helperstartdaily = "* * * "
                self.setStartTime(0)
            elif answer == 1:
                self.session.openWithCallback(self.startday, startdaydialog, _("Select day!"))
        else:
            self.session.open(MessageBox, _("cron is missing - installing it now"), type = MessageBox.TYPE_INFO, timeout = 30)
            os.system("opkg update && opkg install busybox-cron")

    def setStartTime(self, entry):
        if entry is not None and entry >= 0:
            self.selectedEntry = entry
            self.starttime=ConfigClock(default = time())
            dlg = self.session.openWithCallback(self.TimeInputClosed, PBTimeInput, self.starttime)
            dlg.setTitle(_("Please change starttime"))

    def TimeInputClosed(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.helpstring = strftime("%T", localtime(ret[1]))
                self.restime = self.helpstring.split(":")
                ltr = self.restime[1] + " " + self.restime[0] + " " + self.helperstartdaily + "%s \n" % self.userkit
                print ltr
                if os.path.isfile("/etc/cron/crontabs/root"):
                    f = open("/etc/cron/crontabs/root", "r")
                    helper = f.readlines()
                    f.close()
                else:
                    helper = ""
                f = open("/etc/cron/crontabs/root", "w")
                for line in helper:
                    if self.userkit not in line:
                        f.write(line)
                f.write(ltr)
                f.close()
                self.session.open(MessageBox, _("%s will start every day at %s") % (self.userkit, self.helpstring), type = MessageBox.TYPE_INFO, timeout = 10)
                print "scriptstart taeglich ein"

    def setStartTime2(self, entry):
        if entry is not None and entry >= 0:
            self.selectedEntry = entry
            self.starttime=ConfigClock(default = time())
            dlg = self.session.openWithCallback(self.TimeInputClosed2, PBTimeInput, self.starttime)
            dlg.setTitle(_("Please change starttime"))

    def TimeInputClosed2(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.helpstring = strftime("%T", localtime(ret[1]))
                self.restime = self.helpstring.split(":")
                ltr = self.restime[1] + " " + self.restime[0] + " " + self.helperstartday + "%s \n" % self.userkit
                print ltr
                if os.path.isfile("/etc/cron/crontabs/root"):
                    f = open("/etc/cron/crontabs/root", "r")
                    helper = f.readlines()
                    f.close()
                else:
                    helper = ""
                f = open("/etc/cron/crontabs/root", "w")
                for line in helper:
                    if self.userkit not in line:
                        f.write(line)
                f.write(ltr)
                f.close()
                self.session.open(MessageBox, _("%s will start every week on %s at %s") % (self.userkit, self.meshelperstartday, self.helpstring), type = MessageBox.TYPE_INFO, timeout = 10)
                print "Scriptstart woechentlich ein"

    def delstart(self, answer):
        if answer is None:
            self.session.open(MessageBox,_("action canceled"), MessageBox.TYPE_ERROR)
        if answer is False:
            self.session.open(MessageBox,_("action canceled"), MessageBox.TYPE_ERROR)
        else:
            if os.path.isfile("/etc/cron/crontabs/root"):
                f = open("/etc/cron/crontabs/root", "r")
                helper = f.readlines()
                f.close()
            else:
                helper = ""
            f = open("/etc/cron/crontabs/root", "w")
            for line in helper:
                if self.userkit not in line:
                    f.write(line)
            f.close()
            self.session.open(MessageBox, _("Starting of %s is switched to off!") % self.userkit, type = MessageBox.TYPE_INFO, timeout = 10)
            print "Skriptstart aus"

    def startday(self, answer):
        print "answer:", answer
        if answer == 0:
            self.helperstartday = "* * 0 "
            self.meshelperstartday = _("Sunday")
            self.setStartTime2(0)
        elif answer == 1:
            self.helperstartday = "* * 1 "
            self.meshelperstartday = _("Monday")
            self.setStartTime2(0)
        elif answer == 2:
            self.helperstartday = "* * 2 "
            self.meshelperstartday = _("Tuesday")
            self.setStartTime2(0)
        elif answer == 3:
            self.helperstartday = "* * 3 "
            self.meshelperstartday = _("Wednesday")
            self.setStartTime2(0)
        elif answer == 4:
            self.helperstartday = "* * 4 "
            self.meshelperstartday = _("Thursday")
            self.setStartTime2(0)
        elif answer == 5:
            self.helperstartday = "* * 5 "
            self.meshelperstartday = _("Friday")
            self.setStartTime2(0)
        elif answer == 6:
            self.helperstartday = "* * 6 "
            self.meshelperstartday = _("Saturday")
            self.setStartTime2(0)

    def UserScriptPerformstart(self,answer):
        print "answer:", answer
        if answer == 0:
            name = os.path.basename(self.userkit)
            cmd1 = "ln -s /usr/script/%s /etc/init.d/%s" % (name, name)
            os.system(cmd1)
            cmd2 = "ln -s /etc/init.d/%s /etc/rc2.d/S99%s" % (name, name)
            os.system(cmd2)
        elif answer == 1:
            self.session.openWithCallback(self.UserScriptPerform2,MessageBox,_("Execute %s ?") % self.userkit,MessageBox.TYPE_YESNO)
    
    def UserScriptDelete(self,answer):
        name = os.path.basename(self.userkit)
        ininit = os.listdir("/etc/init.d")
        osstart = os.listdir("/etc/rc2.d")
        helper = "/etc/init.d/" + name
        helper2 = "/etc/rc2.d/S99" + name
        if answer is None:
            self.skipUserScript(_("answer is None"))
        if answer is False:
            self.skipUserScript(_("you were not confirming"))
        else:
            if os.path.islink(helper):
                os.unlink(helper)
            if os.path.islink(helper2):
                os.unlink(helper2)


    def UserScriptPerform(self,answer):
        if answer is None:
            self.skipUserScript(_("answer is None"))
        if answer is False:
            self.skipUserScript(_("you were not confirming"))
        else:
            title = _("executing %s" %(self.userkit))
            cmd = "%s"  % (self.userkit)
            self.session.open(PBConsole2,_(title),[cmd])
            
    def UserScriptPerform2(self,answer):
        if answer is None:
            self.skipUserScript(_("answer is None"))
        if answer is False:
            self.skipUserScript(_("you were not confirming"))
        else:
            title = _("executing %s" %(self.userkit))
            cmd = "%s &"  % (self.userkit)
            self.session.open(PBConsole2,_(title),[cmd])

    def skipUserScript(self,reason):
        self.session.open(MessageBox,_("executing was canceled, because %s") % reason, MessageBox.TYPE_ERROR)

    def getUserScriptList(self):
        userkits = []
        for kitfile in os.listdir("/tmp"):
            if kitfile.endswith(".sh") is True: 
                userkits.append(( kitfile, "/tmp/%s" % kitfile ))
        if os.path.exists("/usr/script"):
            for kitfile in os.listdir("/usr/script"):
                if kitfile.endswith(".sh") is True: 
                    userkits.append(( kitfile, "/usr/script/%s" % kitfile ))

        return userkits

    def cancel(self):
        print "\n[menu] cancel\n"
        self.close(None)

class DialogWhatTodo(Screen):
    skin = """
        <screen name="DialogWhatTodo" position="60,245" size="800,10" title="PB-Script-Starter">
        <widget name="text" position="65,8" size="650,0" font="Regular;22" />
        <widget name="QuestionPixmap" pixmap="skin_default/icons/input_question.png" position="5,5" size="53,53" alphatest="on" />
        <widget name="list" position="100,100" size="550,375" />
        <applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth = self.instance.size().width()
orgpos = self.instance.position()
textsize = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 50)
offset = 0
offset = 120
wsizex = textsize[0] + 200
wsizey = textsize[1] + offset
if (280 &gt; wsizex):
    wsizex = 280
wsize = (wsizex, wsizey)


# resize
self.instance.resize(eSize(*wsize))

# resize label
self[&quot;text&quot;].instance.resize(eSize(*textsize))

# move list
listsize = (wsizex, 50)
self[&quot;list&quot;].instance.move(ePoint(0, textsize[1]))
self[&quot;list&quot;].instance.resize(eSize(*listsize))

# center window
newwidth = wsize[0]
self.instance.move(ePoint(orgpos.x() + (orgwidth - newwidth)/2, orgpos.y()))
        </applet>
    </screen>"""

    def __init__(self, session, text, userkit):
        Screen.__init__(self, session)
        self["text"] = Label(text)
        self["Text"] = StaticText(text)
        self.text = text
        self["QuestionPixmap"] = Pixmap()
        self.userkit=userkit[1]
        name = os.path.basename(self.userkit)
        ininit = os.listdir("/etc/init.d")
        osstart = os.listdir("/etc/rc2.d")
        self.list = []
        if "usr/script" in self.userkit and not name in ininit and not name in osstart:
            self.list.append((_("How to execute %s?") % self.userkit, 0))
        if "usr/script" in self.userkit and name in ininit:
            self.list.append((_("Remove %s from autostart?") % self.userkit, 1))
        if os.path.isfile("/etc/cron/crontabs/root"):
            if self.userkit in open("/etc/cron/crontabs/root").read():
                self.list.append((_("switch off starting of %s?") % self.userkit, 2))
        self["list"] = MenuList(self.list)
        self["actions"] = ActionMap(["MsgBoxActions", "DirectionActions"], 
            {
                "cancel": self.cancel,
                "ok": self.ok,
                "up": self.up,
                "down": self.down,
                "left": self.left,
                "right": self.right,
                "upRepeated": self.up,
                "downRepeated": self.down,
                "leftRepeated": self.left,
                "rightRepeated": self.right
            }, -1)

    def __onShown(self):
        self.onShown.remove(self.__onShown)
    def cancel(self):
        self.close(-1)
    def ok(self):
        self.close(self["list"].getCurrent()[1])
    def up(self):
        self.move(self["list"].instance.moveUp)
    def down(self):
        self.move(self["list"].instance.moveDown)
    def left(self):
        self.move(self["list"].instance.pageUp)
    def right(self):
        self.move(self["list"].instance.pageDown)
    def move(self, direction):
        self["list"].instance.moveSelection(direction)
    def __repr__(self):
        return str(type(self)) + "(" + self.text + ")"

class DialogPeriodstart(Screen):

        skin = """
                <screen name="DialogPeriodstart" position="60,245" size="600,10" title="PB-Script-Starter">
                <widget name="text" position="65,8" size="520,0" font="Regular;22" />
                <widget name="QuestionPixmap" pixmap="skin_default/icons/input_question.png" position="5,5" size="53,53" alphatest="on" />
                <widget name="list" position="100,100" size="480,375" />
                <applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth = self.instance.size().width()
orgpos = self.instance.position()
textsize = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 50)
offset = 0
offset = 90
wsizex = textsize[0] + 60
wsizey = textsize[1] + offset
if (280 &gt; wsizex):
        wsizex = 280
wsize = (wsizex, wsizey)


# resize
self.instance.resize(eSize(*wsize))

# resize label
self[&quot;text&quot;].instance.resize(eSize(*textsize))

# move list
listsize = (wsizex, 80)
self[&quot;list&quot;].instance.move(ePoint(0, textsize[1]))
self[&quot;list&quot;].instance.resize(eSize(*listsize))

# center window
newwidth = wsize[0]
self.instance.move(ePoint(orgpos.x() + (orgwidth - newwidth)/2, orgpos.y()))
                </applet>
        </screen>"""

        def __init__(self, session, text,):
                Screen.__init__(self, session)
                self["text"] = Label(text)
                self["Text"] = StaticText(text)
                self.text = text
                self["QuestionPixmap"] = Pixmap()
                self.list = []
                self.list = [ (_("Daily"), 0), (_("Weekly"), 1) ]
                self["list"] = MenuList(self.list)
                self["actions"] = ActionMap(["MsgBoxActions", "DirectionActions"], 
                        {
                                "cancel": self.cancel,
                                "ok": self.ok,
                                "up": self.up,
                                "down": self.down,
                                "left": self.left,
                                "right": self.right,
                                "upRepeated": self.up,
                                "downRepeated": self.down,
                                "leftRepeated": self.left,
                                "rightRepeated": self.right
                        }, -1)

        def __onShown(self):
                self.onShown.remove(self.__onShown)
        def cancel(self):
                self.close(-1)
        def ok(self):
                self.close(self["list"].getCurrent()[1])
        def up(self):
                self.move(self["list"].instance.moveUp)
        def down(self):
                self.move(self["list"].instance.moveDown)
        def left(self):
                self.move(self["list"].instance.pageUp)
        def right(self):
                self.move(self["list"].instance.pageDown)
        def move(self, direction):
                self["list"].instance.moveSelection(direction)
        def __repr__(self):
                return str(type(self)) + "(" + self.text + ")"

class startdaydialog(Screen):

        skin = """
                <screen name="startdaydialog" position="60,245" size="600,10" title="PB-Script-Starter">
                <widget name="text" position="65,8" size="520,0" font="Regular;22" />
                <widget name="QuestionPixmap" pixmap="skin_default/icons/input_question.png" position="5,5" size="53,53" alphatest="on" />
                <widget name="list" position="100,100" size="480,375" />
                <applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth = self.instance.size().width()
orgpos = self.instance.position()
textsize = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 50)
offset = 0
offset = 200
wsizex = textsize[0] + 60
wsizey = textsize[1] + offset
if (280 &gt; wsizex):
        wsizex = 280
wsize = (wsizex, wsizey)


# resize
self.instance.resize(eSize(*wsize))

# resize label
self[&quot;text&quot;].instance.resize(eSize(*textsize))

# move list
listsize = (wsizex, 190)
self[&quot;list&quot;].instance.move(ePoint(0, textsize[1]))
self[&quot;list&quot;].instance.resize(eSize(*listsize))

# center window
newwidth = wsize[0]
self.instance.move(ePoint(orgpos.x() + (orgwidth - newwidth)/2, orgpos.y()))
                </applet>
        </screen>"""

        def __init__(self, session, text,):
                Screen.__init__(self, session)
                self["text"] = Label(text)
                self["Text"] = StaticText(text)
                self.text = text
                self["QuestionPixmap"] = Pixmap()
                self.list = []
                self.list = [ (_("Sunday"), 0), (_("Monday"), 1), (_("Tuesday"), 2), (_("Wednesday"), 3), (_("Thursday"), 4), (_("Friday"), 5), (_("Saturday"), 6) ]
                self["list"] = MenuList(self.list)
                self["actions"] = ActionMap(["MsgBoxActions", "DirectionActions"], 
                        {
                                "cancel": self.cancel,
                                "ok": self.ok,
                                "up": self.up,
                                "down": self.down,
                                "left": self.left,
                                "right": self.right,
                                "upRepeated": self.up,
                                "downRepeated": self.down,
                                "leftRepeated": self.left,
                                "rightRepeated": self.right
                        }, -1)

        def __onShown(self):
                self.onShown.remove(self.__onShown)
        def cancel(self):
                self.close(-1)
        def ok(self):
                self.close(self["list"].getCurrent()[1])
        def up(self):
                self.move(self["list"].instance.moveUp)
        def down(self):
                self.move(self["list"].instance.moveDown)
        def left(self):
                self.move(self["list"].instance.pageUp)
        def right(self):
                self.move(self["list"].instance.pageDown)
        def move(self, direction):
                self["list"].instance.moveSelection(direction)
        def __repr__(self):
                return str(type(self)) + "(" + self.text + ")"

class DialogPerformever(Screen):

    skin = """
        <screen name="DialogPerformever" position="60,245" size="600,10" title="PB-Script-Starter">
        <widget name="text" position="65,8" size="520,0" font="Regular;22" />
        <widget name="QuestionPixmap" pixmap="skin_default/icons/input_question.png" position="5,5" size="53,53" alphatest="on" />
        <widget name="list" position="100,100" size="480,375" />
        <applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth = self.instance.size().width()
orgpos = self.instance.position()
textsize = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 50)
offset = 0
offset = 120
wsizex = textsize[0] + 60
wsizey = textsize[1] + offset
if (280 &gt; wsizex):
    wsizex = 280
wsize = (wsizex, wsizey)


# resize
self.instance.resize(eSize(*wsize))

# resize label
self[&quot;text&quot;].instance.resize(eSize(*textsize))

# move list
listsize = (wsizex, 100)
self[&quot;list&quot;].instance.move(ePoint(0, textsize[1]))
self[&quot;list&quot;].instance.resize(eSize(*listsize))

# center window
newwidth = wsize[0]
self.instance.move(ePoint(orgpos.x() + (orgwidth - newwidth)/2, orgpos.y()))
        </applet>
    </screen>"""

    def __init__(self, session, text,):
        Screen.__init__(self, session)
        self["text"] = Label(text)
        self["Text"] = StaticText(text)
        self.text = text
        self["QuestionPixmap"] = Pixmap()
        self.list = []
        self.list = [ (_("Execute permanently"), 0), (_("run periodically"), 1), (_("only run once"), 2) ]
        self["list"] = MenuList(self.list)
        self["actions"] = ActionMap(["MsgBoxActions", "DirectionActions"], 
            {
                "cancel": self.cancel,
                "ok": self.ok,
                "up": self.up,
                "down": self.down,
                "left": self.left,
                "right": self.right,
                "upRepeated": self.up,
                "downRepeated": self.down,
                "leftRepeated": self.left,
                "rightRepeated": self.right
            }, -1)

    def __onShown(self):
        self.onShown.remove(self.__onShown)
    def cancel(self):
        self.close(-1)
    def ok(self):
        self.close(self["list"].getCurrent()[1])
    def up(self):
        self.move(self["list"].instance.moveUp)
    def down(self):
        self.move(self["list"].instance.moveDown)
    def left(self):
        self.move(self["list"].instance.pageUp)
    def right(self):
        self.move(self["list"].instance.pageDown)
    def move(self, direction):
        self["list"].instance.moveSelection(direction)
    def __repr__(self):
        return str(type(self)) + "(" + self.text + ")"


class DialogPerformstart(Screen):

    skin = """
        <screen name="DialogPerformstart" position="60,245" size="600,10" title="PB-Script-Starter">
        <widget name="text" position="65,8" size="520,0" font="Regular;22" />
        <widget name="QuestionPixmap" pixmap="skin_default/icons/input_question.png" position="5,5" size="53,53" alphatest="on" />
        <widget name="list" position="100,100" size="480,375" />
        <applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth = self.instance.size().width()
orgpos = self.instance.position()
textsize = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 50)
offset = 0
offset = 80
wsizex = textsize[0] + 100
wsizey = textsize[1] + offset
if (280 &gt; wsizex):
    wsizex = 280
wsize = (wsizex, wsizey)


# resize
self.instance.resize(eSize(*wsize))

# resize label
self[&quot;text&quot;].instance.resize(eSize(*textsize))

# move list
listsize = (wsizex, 50)
self[&quot;list&quot;].instance.move(ePoint(0, textsize[1]))
self[&quot;list&quot;].instance.resize(eSize(*listsize))

# center window
newwidth = wsize[0]
self.instance.move(ePoint(orgpos.x() + (orgwidth - newwidth)/2, orgpos.y()))
        </applet>
    </screen>"""

    def __init__(self, session, text,):
        Screen.__init__(self, session)
        self["text"] = Label(text)
        self["Text"] = StaticText(text)
        self.text = text
        self["QuestionPixmap"] = Pixmap()
        self.list = []
        self.list = [ (_("Execute every startup"), 0), (_("only run this time permanently"), 1) ]
        self["list"] = MenuList(self.list)
        self["actions"] = ActionMap(["MsgBoxActions", "DirectionActions"], 
            {
                "cancel": self.cancel,
                "ok": self.ok,
                "up": self.up,
                "down": self.down,
                "left": self.left,
                "right": self.right,
                "upRepeated": self.up,
                "downRepeated": self.down,
                "leftRepeated": self.left,
                "rightRepeated": self.right
            }, -1)

    def __onShown(self):
        self.onShown.remove(self.__onShown)
    def cancel(self):
        self.close(-1)
    def ok(self):
        self.close(self["list"].getCurrent()[1])
    def up(self):
        self.move(self["list"].instance.moveUp)
    def down(self):
        self.move(self["list"].instance.moveDown)
    def left(self):
        self.move(self["list"].instance.pageUp)
    def right(self):
        self.move(self["list"].instance.pageDown)
    def move(self, direction):
        self["list"].instance.moveSelection(direction)
    def __repr__(self):
        return str(type(self)) + "(" + self.text + ")"


###########################################################################
def SimpleEntry(name, picture):
    res = [(name, picture)]
    #res = []
    picture = ('/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/' + picture)
    if name == "---":
        if fileExists(picture):
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 22), size=(470, 4), png=loadPNG(picture)))
    else:
        if fileExists(picture):
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(48, 48), png=loadPNG(picture)))
    # Estuary - Start Here
    if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
        res.append(MultiContentEntryText(pos=(60, 5), size=(800, 38), font=0, text=name))
    else:
    # Estuary - End Here
        res.append(MultiContentEntryText(pos=(60, 10), size=(450, 38), font=0, text=name))

    return res

class ExtrasList(MenuList, HTMLComponent, GUIComponent):
    def __init__(self, list, enableWrapAround = False):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.list = list
        self.l.setList(list)
        # Estuary - Start Here 
        if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
            self.l.setFont(0, gFont('Regular', 27))
        else:
        # Estuary - Cut Here (next line one Tab back)
            self.l.setFont(0, gFont('Regular', 21))
        self.l.setItemHeight(48)
        self.onSelectionChanged = []
        self.enableWrapAround = enableWrapAround
        self.last = 0

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)
        if self.enableWrapAround:
            self.instance.setWrapAround(True)

    def selectionChanged(self):
        isDiv = False
        try:
            for element in self.list[self.getSelectionIndex()]:
                if element[0] == "---":
                    isDiv = True
                    if self.getSelectionIndex() < self.last:
                        self.up()
                    else:
                        self.down()
        except Exception, e:
            pass

        self.last = self.getSelectionIndex()
        if not isDiv:
            for f in self.onSelectionChanged:
                f()
