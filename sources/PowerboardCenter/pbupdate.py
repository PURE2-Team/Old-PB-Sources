# 2013-04-19
# edit 2013-06-23
#@author: stibbich <stibbich@pb-powerboard.com>
#Edited by Franc 25.05.2016 / 12.11.2016
#
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

from enigma import *
from Tools.Directories import fileExists
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Screens.SoftwareUpdate import UpdatePlugin
from Plugins.Extensions.PowerboardCenter.PBCon import PBConsole2
from Components.Input import Input
from Components.Button import Button
import os
import gettext
import re
from time import *

from Plugins.Extensions.PowerboardCenter.PBTimeInput import PBTimeInput
from Tools.Directories import resolveFilename, SCOPE_ACTIVE_SKIN



#************************************************************************************************************************************** 
import sys
from Components.Sources.List import List

#************************************************************************************************************************************** 




class PBUpdate(Screen):
    skin = """
        <screen name="PBUpdate" position="center,center" size="850,420" title="PB-Auto-Update" flags="wfNoBorder">
            <widget name="menu" position="45,74" size="650,300" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="Configure Autoupdate" position="20,8" size="485,50" font="Regular;28" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
            l.append(self.buildListEntry(_("When to show if update is available"), _("Please choose..."), "addon.png"))
            l.append(self.buildListEntry(_("When to do automatic update"), _("Please choose..."), "addon.png"))
            l.append(self.buildListEntry(_("Update the box NOW"), _("Please choose..."), "addon.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
        else:
            est = False
            list = []
            list.append(SimpleEntry(_("When to show if update is available"), "system.png"))
            list.append(SimpleEntry(_("When to do automatic update"), "system.png"))
            list.append(SimpleEntry(_("Update the box NOW"), "system.png"))
            self['menu'] = ExtrasList(list)
			
#************************************************************************************************************************************** 
		
		
		
		

        
        #
		
        self["actions"] = ActionMap(["SetupActions", "OkCancelActions", "ColorActions", "DirectionActions"],
        {
            "red": self.quit,
            "ok": self.go,
            "cancel": self.quit,
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
        if os.path.isfile("/etc/init.d/busybox-cron"):
            if est == True:
                index = self['list'].getSelectedIndex()
            else:
                index = self['menu'].getSelectedIndex()
            if (index == 0):
                self.session.openWithCallback(self.showupdate, showupdatedialog, _("When would you like to search for updates?"))
            elif (index == 1):
                self.session.openWithCallback(self.doupdate, showupdatedialog, _("When would you update the box?"))
            elif (index == 2):
				try:
					self.session.open(UpdatePlugin) 
				except Exception, e:
					print e
					return

        else:
            self.session.open(MessageBox, _("cron is missing - installing it now"), type = MessageBox.TYPE_INFO, timeout = 30)
            os.system("opkg update && opkg install busybox-cron")

    def doupdatenow(self, answer):
        if answer is None:
            self.session.open(MessageBox,_("action canceled"), MessageBox.TYPE_ERROR)
        if answer is False:
            self.session.open(MessageBox,_("action canceled"), MessageBox.TYPE_ERROR)
        else:
            self.session.open(PBConsole2,_("Classic Systemupdate"),["opkg update && opkg upgrade"])
    
    def deldoupdate(self, answer):
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
                if "pbupdate.sh update" not in line:
                    f.write(line)
            f.close()
            self.session.open(MessageBox, _("Autoupdate is switched to off!"), type = MessageBox.TYPE_INFO, timeout = 10)
            print "update aus"

    def delshowupdate(self, answer):
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
                if "showonly" not in line:
                    f.write(line)
            f.close()
            self.session.open(MessageBox, _("Updatemessage is switched to off!"), type = MessageBox.TYPE_INFO, timeout = 10)
            print "updatemessage aus"

    def doupdate(self, answer):
        print "answer:", answer
        if answer == 0:
            self.helperdodaily = "* * * "
            self.setupdatetime(0)
        elif answer == 1:
            self.session.openWithCallback(self.doupdateday, showupdatedaydialog, _("Select day!"))
        elif answer == 2:
            self.session.openWithCallback(self.deldoupdate,MessageBox,_("switch off autoupdate?"),MessageBox.TYPE_YESNO)

    def setupdatetime(self, entry):
        if entry is not None and entry >= 0:
            self.selectedEntry = entry
            self.updatetime=ConfigClock(default = time())
            dlg = self.session.openWithCallback(self.UpdateTimeInputClosed, PBTimeInput, self.updatetime)
            dlg.setTitle(_("Please choose updatetime"))

    def UpdateTimeInputClosed(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.helpstring = strftime("%T", localtime(ret[1]))
                self.updtime = self.helpstring.split(":")
                ltr = self.updtime[1] + " " + self.updtime[0] + " " + self.helperdodaily + "/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/pbupdate.sh update \n"
                print ltr
                if os.path.isfile("/etc/cron/crontabs/root"):
                    f = open("/etc/cron/crontabs/root", "r")
                    helper = f.readlines()
                    f.close()
                else:
                    helper = ""
                f = open("/etc/cron/crontabs/root", "w")
                for line in helper:
                    if "pbupdate.sh update" not in line:
                        f.write(line)
                f.write(ltr)
                f.close()
                self.session.open(MessageBox, _("Box will be updated every day at %s") % self.helpstring, type = MessageBox.TYPE_INFO, timeout = 10)
                print "update taeglich ein"

    def setupdatetime2(self, entry):
        if entry is not None and entry >= 0:
            self.selectedEntry = entry
            self.updatetime=ConfigClock(default = time())
            dlg = self.session.openWithCallback(self.UpdateTimeInputClosed2, PBTimeInput, self.updatetime)
            dlg.setTitle(_("Please choose updatetime"))

    def UpdateTimeInputClosed2(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.helpstring = strftime("%T", localtime(ret[1]))
                self.updtime = self.helpstring.split(":")
                ltr = self.updtime[1] + " " + self.updtime[0] + " " + self.helperdoday + "/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/pbupdate.sh update \n"
                print ltr
                if os.path.isfile("/etc/cron/crontabs/root"):
                    f = open("/etc/cron/crontabs/root", "r")
                    helper = f.readlines()
                    f.close()
                else:
                    helper = ""
                f = open("/etc/cron/crontabs/root", "w")
                for line in helper:
                    if "pbupdate.sh update" not in line:
                        f.write(line)
                f.write(ltr)
                f.close()
                self.session.open(MessageBox, _("Box will be updated every week on %s at %s") % (self.meshelperdoday, self.helpstring), type = MessageBox.TYPE_INFO, timeout = 10)
                print "update woechentlich ein"


    def doupdateday(self, answer):
        print "answer:", answer
        if answer == 0:
            self.helperdoday = "* * 0 "
            self.meshelperdoday = _("Sunday")
            self.setupdatetime2(0)
        elif answer == 1:
            self.helperdoday = "* * 1 "
            self.meshelperdoday = _("Monday")
            self.setupdatetime2(0)
        elif answer == 2:
            self.helperdoday = "* * 2 "
            self.meshelperdoday = _("Tuesday")
            self.setupdatetime2(0)
        elif answer == 3:
            self.helperdoday = "* * 3 "
            self.meshelperdoday = _("Wednesday")
            self.setupdatetime2(0)
        elif answer == 4:
            self.helperdoday = "* * 4 "
            self.meshelperdoday = _("Thursday")
            self.setupdatetime2(0)
        elif answer == 5:
            self.helperdoday = "* * 5 "
            self.meshelperdoday = _("Friday")
            self.setupdatetime2(0)
        elif answer == 6:
            self.helperdoday = "* * 6 "
            self.meshelperdoday = _("Saturday")
            self.setupdatetime2(0)

    def showupdate(self, answer):
        print "answer:", answer
        if answer == 0:
            self.helperdaily = "* * * "
            self.setshowtime(0)
        elif answer == 1:
            self.session.openWithCallback(self.showupdateday, showupdatedaydialog, _("Select day!"))
        elif answer == 2:
            self.session.openWithCallback(self.delshowupdate,MessageBox,_("switch off show updatemessage?"),MessageBox.TYPE_YESNO)

    def setshowtime(self, entry):
        if entry is not None and entry >= 0:
            self.selectedEntry = entry
            self.showupdatetime=ConfigClock(default = time())
            dlg = self.session.openWithCallback(self.ShowTimeInputClosed, PBTimeInput, self.showupdatetime)
            dlg.setTitle(_("Choose time for updatemessage"))

    def ShowTimeInputClosed(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.helpstring = strftime("%T", localtime(ret[1]))
                self.updtime = self.helpstring.split(":")
                ltr = self.updtime[1] + " " + self.updtime[0] + " " + self.helperdaily + "/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/pbupdate.sh showonly \n"
                print ltr
                if os.path.isfile("/etc/cron/crontabs/root"):
                    f = open("/etc/cron/crontabs/root", "r")
                    helper = f.readlines()
                    f.close()
                else:
                    helper = ""
                f = open("/etc/cron/crontabs/root", "w")
                for line in helper:
                    if "pbupdate.sh showonly" not in line:
                        f.write(line)
                f.write(ltr)
                f.close()
                self.session.open(MessageBox, _("Updatemessage will be shown every day at %s") % self.helpstring, type = MessageBox.TYPE_INFO, timeout = 10)
                print "updatemessage taeglich ein"

    def setshowtime2(self, entry):
        if entry is not None and entry >= 0:
            self.selectedEntry = entry
            self.updatetime=ConfigClock(default = time())
            dlg = self.session.openWithCallback(self.ShowTimeInputClosed2, PBTimeInput, self.updatetime)
            dlg.setTitle(_("Choose time for updatemessage"))

    def ShowTimeInputClosed2(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.helpstring = strftime("%T", localtime(ret[1]))
                self.updtime = self.helpstring.split(":")
                ltr = self.updtime[1] + " " + self.updtime[0] + " " + self.helperday + "/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/pbupdate.sh showonly \n"
                print ltr
                if os.path.isfile("/etc/cron/crontabs/root"):
                    f = open("/etc/cron/crontabs/root", "r")
                    helper = f.readlines()
                    f.close()
                else:
                    helper = ""
                f = open("/etc/cron/crontabs/root", "w")
                for line in helper:
                    if "pbupdate.sh showonly" not in line:
                        f.write(line)
                f.write(ltr)
                f.close()
                self.session.open(MessageBox, _("Updatemessage will be shown every week on %s at %s") % (self.meshelperday, self.helpstring), type = MessageBox.TYPE_INFO, timeout = 10)
                print "updatemessage woechentlich ein"

    def showupdateday(self, answer):
        print "answer:", answer
        if answer == 0:
            self.helperday = "* * 0 "
            self.meshelperday = _("Sunday")
            self.setshowtime2(0)
        elif answer == 1:
            self.helperday = "* * 1 "
            self.meshelperday = _("Monday")
            self.setshowtime2(0)
        elif answer == 2:
            self.helperday = "* * 2 "
            self.meshelperday = _("Tuesday")
            self.setshowtime2(0)
        elif answer == 3:
            self.helperday = "* * 3 "
            self.meshelperday = _("Wednesday")
            self.setshowtime2(0)
        elif answer == 4:
            self.helperday = "* * 4 "
            self.meshelperday = _("Thursday")
            self.setshowtime2(0)
        elif answer == 5:
            self.helperday = "* * 5 "
            self.meshelperday = _("Friday")
            self.setshowtime2(0)
        elif answer == 6:
            self.helperday = "* * 6 "
            self.meshelperday = _("Saturday")
            self.setshowtime2(0)

    def cancel(self):
        print "\n[menu] cancel\n"
        self.close(None)
		
    def quit(self):
        self.close()


class showupdatedaydialog(Screen):

        skin = """
                <screen name="showupdatedaydialog" position="60,245" size="600,10" title="PB-Autoupdater">
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


class showupdatedialog(Screen):

        skin = """
                <screen name="showupdatedialog" position="60,245" size="600,10" title="PB-Autoupdater">
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
                self.list = [ (_("Daily"), 0), (_("Weekly"), 1), (_("Off"), 2) ]
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
        res.append(MultiContentEntryText(pos=(60, 5), size=(600, 38), font=0, text=name))
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
