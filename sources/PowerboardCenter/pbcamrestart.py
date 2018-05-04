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

from enigma import *
from Tools.Directories import fileExists, resolveFilename, SCOPE_ACTIVE_SKIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
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


class PBCamRestart(Screen):
    skin = """
        <screen name="PBCamRestart" position="center,center" size="850,420" title="PB-Cam-Restarter" flags="wfNoBorder">
            <widget name="menu" position="45,74" size="650,300" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="automatically restart cam" position="20,8" size="485,50" font="Regular;28" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
		
		
        # list = []

        # list.append(SimpleEntry(_("Configure camrestart"), "system.png"))


		
        global est
        est = False				
		
		
		
#************************************************************************************************************************************** 
	    # Estuary - Start Here	
        self["page"] = Label()
        self["page"].setText(" ")

        if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
            est = True
            l = []
            l.append(self.buildListEntry(_("Configure camrestart"), _("Configure how to handle script"), "syssetup.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
        else:
            est = False
            list = []
            list.append(SimpleEntry(_("Configure camrestart"), "system.png"))
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
        if os.path.isfile("/etc/init.d/busybox-cron"):
            a = "/usr/script/cam"
            b = os.path.isdir(a)
            c = False
            g = True
            h = False
            d = os.path.isfile("/etc/clist.list")
            if d:
                e = open("/etc/clist.list")
                f = e.read()
                if "no" in f:
                    g = False
            if b:
                c = [os.listdir(a)]
                c = []
            if b is True and c is not False and d is not False and g is not False:
                if est == True:
                    index = self['list'].getSelectedIndex()
                else:
                    index = self['menu'].getSelectedIndex()
                if (index == 0):
                    self.session.openWithCallback(self.camrestart, camrestartdialog, _("When should the cam restart?"))
            else:
                self.session.open(MessageBox, _("There is no cam to restart - install and/or start one!"), type = MessageBox.TYPE_INFO, timeout = 10)
        else:
            self.session.open(MessageBox, _("cron is missing - installing it now"), type = MessageBox.TYPE_INFO, timeout = 30)
            os.system("opkg update && opkg install busybox-cron")


    def camrestart(self, answer):
        print "answer:", answer
        if answer == 0:
            self.helperrestartdaily = "* * * "
            self.setRestartTime(0)
        elif answer == 1:
            self.session.openWithCallback(self.restartday, restartdaydialog, _("Select day!"))
        elif answer == 2:
            self.session.openWithCallback(self.delrestart,MessageBox,_("switch off camrestart?"),MessageBox.TYPE_YESNO)

    def setRestartTime(self, entry):
        if entry is not None and entry >= 0:
            self.selectedEntry = entry
            self.restarttime=ConfigClock(default = time())
            dlg = self.session.openWithCallback(self.TimeInputClosed, PBTimeInput, self.restarttime)
            dlg.setTitle(_("Please change camrestarttime"))

    def TimeInputClosed(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.helpstring = strftime("%T", localtime(ret[1]))
                self.restime = self.helpstring.split(":")
                ltr = self.restime[1] + " " + self.restime[0] + " " + self.helperrestartdaily + "/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/pbcamrestart.sh \n"
                print ltr
                if os.path.isfile("/etc/cron/crontabs/root"):
                    f = open("/etc/cron/crontabs/root", "r")
                    helper = f.readlines()
                    f.close()
                else:
                    helper = ""
                f = open("/etc/cron/crontabs/root", "w")
                for line in helper:
                    if "pbcamrestart.sh" not in line:
                        f.write(line)
                f.write(ltr)
                f.close()
                self.session.open(MessageBox, _("Cam will be restarted every day at %s") % self.helpstring, type = MessageBox.TYPE_INFO, timeout = 10)
                print "restart cam taeglich ein"

    def setRestartTime2(self, entry):
        if entry is not None and entry >= 0:
            self.selectedEntry = entry
            self.restarttime=ConfigClock(default = time())
            dlg = self.session.openWithCallback(self.TimeInputClosed2, PBTimeInput, self.restarttime)
            dlg.setTitle(_("Please change camrestarttime"))

    def TimeInputClosed2(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.helpstring = strftime("%T", localtime(ret[1]))
                self.restime = self.helpstring.split(":")
                ltr = self.restime[1] + " " + self.restime[0] + " " + self.helperrestartday + "/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/pbcamrestart.sh \n"
                print ltr
                if os.path.isfile("/etc/cron/crontabs/root"):
                    f = open("/etc/cron/crontabs/root", "r")
                    helper = f.readlines()
                    f.close()
                else:
                    helper = ""
                f = open("/etc/cron/crontabs/root", "w")
                for line in helper:
                    if "pbcamrestart.sh" not in line:
                        f.write(line)
                f.write(ltr)
                f.close()
                self.session.open(MessageBox, _("Cam will be restarted every week on %s at %s") % (self.meshelperrestartday, self.helpstring), type = MessageBox.TYPE_INFO, timeout = 10)
                print "restart cam woechentlich ein"

    def delrestart(self, answer):
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
                if "pbcamrestart.sh" not in line:
                    f.write(line)
            f.close()
            self.session.open(MessageBox, _("Camrestart is switched to off!"), type = MessageBox.TYPE_INFO, timeout = 10)
            print "Camrestart aus"

    def restartday(self, answer):
        print "answer:", answer
        if answer == 0:
            self.helperrestartday = "* * 0 "
            self.meshelperrestartday = _("Sunday")
            self.setRestartTime2(0)
        elif answer == 1:
            self.helperrestartday = "* * 1 "
            self.meshelperrestartday = _("Monday")
            self.setRestartTime2(0)
        elif answer == 2:
            self.helperrestartday = "* * 2 "
            self.meshelperrestartday = _("Tuesday")
            self.setRestartTime2(0)
        elif answer == 3:
            self.helperrestartday = "* * 3 "
            self.meshelperrestartday = _("Wednesday")
            self.setRestartTime2(0)
        elif answer == 4:
            self.helperrestartday = "* * 4 "
            self.meshelperrestartday = _("Thursday")
            self.setRestartTime2(0)
        elif answer == 5:
            self.helperrestartday = "* * 5 "
            self.meshelperrestartday = _("Friday")
            self.setRestartTime2(0)
        elif answer == 6:
            self.helperrestartday = "* * 6 "
            self.meshelperrestartday = _("Saturday")
            self.setRestartTime2(0)

    def cancel(self):
        print "\n[menu] cancel\n"
        self.close(None)

class restartdaydialog(Screen):

        skin = """
                <screen name="restartdaydialog" position="60,245" size="600,10" title="PB-Cam-Restarter">
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

class camrestartdialog(Screen):

        skin = """
                <screen name="camrestartdialog" position="60,245" size="600,10" title="PB-Cam-Restarter">
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
