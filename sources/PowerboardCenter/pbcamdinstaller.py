# 2011-10-16
# modifiziert by delfi 10.03.2013
#Edited by Franc 25.05.2016 / 12.11.2016
#@author: stibbich <stibbich@pb-powerboard.com>
#

Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.Label import Label
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Screens.MessageBox import MessageBox
from Screens.Console import Console
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
from Components.Input import Input
import os
import gettext
import re


#************************************************************************************************************************************** 
import sys
from Components.Sources.List import List
from Components.Button import Button
#************************************************************************************************************************************** 




class PBCamdinstaller(Screen):
    skin = """
        <screen name="PBCamdinstaller" position="center,center" size="650,420" title="PB Camd Installer" flags="wfNoBorder">
            <widget name="menu" position="45,84" size="425,300" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="Backup / Restore Scripts" position="20,8" size="485,50" font="Regular;32" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
            <widget source="global.CurrentTime" render="Label" position="555,20" size="90,28" font="Regular;23" halign="right" backgroundColor="black" foregroundColor="grey" shadowOffset="-2,-2" shadowColor="black" transparent="1">
               <convert type="ClockToText">Format:%d.%b</convert>
            </widget>
            <widget source="global.CurrentTime" render="Label" position="475,20" size="80,28" font="Regular;23" halign="right" backgroundColor="black" shadowOffset="-2,-2" shadowColor="black" transparent="1">
               <convert type="ClockToText">Default</convert>
            </widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb_small.png" position="480,200" size="150,150" backgroundColor="black" alphatest="blend" />
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
            l.append(self.buildListEntry(_("Install Camd"), _("Install Camd"), "camman.png"))
            l.append(self.buildListEntry(_("Uninstall Camd"), _("Uninstall Camd"), "stop.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
			
        else:
            est = False
            list = []
            list.append(SimpleEntry(_("Install Camd"), "ok.png"))
            list.append(SimpleEntry(_("Uninstall Camd"), "trash.png"))
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
        if est == True:
            index = self['list'].getSelectedIndex()
        else:
            index = self['menu'].getSelectedIndex()
			
        if (index == 0):
            CamdInstall(self.session)
        elif (index == 1):
            CamdUninstall(self.session)

    def cancel(self):
        print "\n[menu] cancel\n"
        self.close(None)


class CamdInstall(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.askForCamd,ChoiceBox,_("Select Camd to install!"),self.getCamdList())

    def askForCamd(self,camtoinstall):
        if camtoinstall is None:
            self.skipCamInstall(_("No Camd selected"))
        else:
            self.camtoinstall=camtoinstall[1]
            print self.camtoinstall
            p = self.camtoinstall.lower()
            print p
            if p.startswith("oscam"):
                self.session.openWithCallback(self.OscamInstallCallback, DialogOscamInstall, _("How to install oscam?"))
            else:
                self.session.openWithCallback(self.UserScriptInstall,MessageBox,_("Install %s?") % self.camtoinstall,MessageBox.TYPE_YESNO)

    def OscamInstallCallback(self, answer):
        print "answer:", answer
        if answer == 0:
            self.session.openWithCallback(self.UserScriptInstall,MessageBox,_("Install %s?") % self.camtoinstall,MessageBox.TYPE_YESNO)
        elif answer == 1:
            self.session.openWithCallback(self.askForCamscript,ChoiceBox,_("Select camscript to add %s?") % self.camtoinstall, self.getCamaddList())

    def askForCamscript(self,camtoadd):
        print camtoadd
        if camtoadd is None:
            self.skipCamInstall(_("No script selected"))
        else:
            self.camtoadd=camtoadd[1]
            self.session.openWithCallback(self.UserOscamAdd,MessageBox,_("Add to %s?") % self.camtoadd,MessageBox.TYPE_YESNO)

    def UserOscamAdd(self,answer):
        print "answer:", answer
        if answer is None:
            self.skipCamInstall(_("answer is None"))
        if answer is False:
            self.skipCamInstall(_("you were not confirming"))
        else:
            cmd = "mv /tmp/camdinstall/%s /usr/bin/cam && chmod 755 /usr/bin/cam/%s"  % (self.camtoinstall, self.camtoinstall)
            os.system(cmd)
            fto = "/usr/script/cam/%s" %(self.camtoadd)
            print fto
            f = open(fto, "r")
            scrl = f.readlines()
            f.close()

            ca1 = "/usr/script/cam/%s%s" %(self.camtoinstall, self.camtoadd)
            f=open(ca1, "w")
            f.write("#!/bin/sh -x\n\n\n")
            ca2 = "OSD=\"%s/%s\"\n" %(self.camtoinstall, self.camtoadd[:-3])
            f.write(ca2)
            ca3 = "PID1=$(pidof %s)\n" %(self.camtoinstall)
            f.write(ca3)
            ca4 = "PID2=$(pidof %s)\n" %(self.camtoadd[:-3])
            f.write(ca4)
            f.write("Action=$1\n\n\n")
            f.write("cam_clean () {")
            f.write("\t\trm -rf /tmp/*.info*\t/tmp/*.tmp*\n")
            f.write("}\n\n\n")
            f.write("cam_handle () {\n")
            f.write("if test -z \"${PID1}\" || test -z \"${PID1}\" ; then\n")
            f.write("\t\t\t\tcam_up;\n")
            f.write("\t\telse\n")
            f.write("\t\t\t\tcam_down;\n")
            f.write("\t\tfi;\n")
            f.write("}\n\n\n")
            f.write("cam_down ()\t{\n")
            ca5 = "\t\tkillall %s\n" % (self.camtoinstall)
            f.write(ca5)
            f.write("\t\tsleep 3\n")
            ca6 = "\t\tkillall %s\n" %(self.camtoadd[:-3])
            f.write(ca6)
            f.write("\t\tcam_clean\n")
            f.write("}\n\n\n")
            f.write("cam_up () {\n")
            ca7 = "\t\t/usr/bin/cam/%s &\n" % (self.camtoinstall)
            f.write(ca7)
            f.write("\tsleep10\n")
            ca8 = "\t\t/usr/bin/cam/%s &\n" %(self.camtoadd[:-3])
            f.write(ca8)
            f.write("}\n\n\n")
            f.write("if test \"$Action\" = \"cam_res\" ; then\n")
            f.write("\t\tcam_down\n")
            f.write("\t\tcam_up\n")
            f.write("elif test \"$Action\" = \"cam_down\" ; then\n")
            f.write("\t\tcam_down\n")
            f.write("elif test \"$Action\" = \"cam_up\" ; then\n")
            f.write("\t\tcam_up\n")
            f.write("else\n")
            f.write("\t\tcam_handle\n")
            f.write("fi\n\n\n")
            f.write("exit 0\n")
            f.close()
            ca9 = "chmod 755 %s" % ca1
            os.system(ca9)
            self.session.open(MessageBox, _("Camd has been added!"), type = MessageBox.TYPE_INFO,timeout = 5)

            
    def UserScriptInstall(self,answer):
        if answer is None:
            self.skipCamInstall(_("answer is None"))
        if answer is False:
            self.skipCamInstall(_("you were not confirming"))
        else:
            cmd = "mv /tmp/camdinstall/%s /usr/bin/cam && chmod 755 /usr/bin/cam/%s"  % (self.camtoinstall, self.camtoinstall)
            os.system(cmd)

            ca1 = "/usr/script/cam/%s.sh" % (self.camtoinstall)
            f=open(ca1, "w")
            f.write("#!/bin/sh -x\n\n\n")
            ca2 = "OSD=\"%s\"\n" % (self.camtoinstall)
            f.write(ca2)
            ca3 = "PID=$(pidof %s)\n" % (self.camtoinstall)
            f.write(ca3)
            f.write("Action=$1\n\n\n")
            f.write("cam_clean () {")
            f.write("\t\trm -rf /tmp/*.info*\t/tmp/*.tmp*\n")
            f.write("}\n\n\n")
            f.write("cam_handle () {\n")
            f.write("\t\tif test\t-z \"${PID}\"\t; then\n")
            f.write("\t\t\t\tcam_up;\n")
            f.write("\t\telse\n")
            f.write("\t\t\t\tcam_down;\n")
            f.write("\t\tfi;\n")
            f.write("}\n\n\n")
            f.write("cam_down ()\t{\n")
            ca4 = "\t\tkillall %s\n" % (self.camtoinstall)
            f.write(ca4)
            f.write("\t\tsleep 2\n")
            f.write("\t\tcam_clean\n")
            f.write("}\n\n\n")
            f.write("cam_up () {\n")
            ca5 = "\t\t/usr/bin/cam/%s &\n" % (self.camtoinstall)
            f.write(ca5)
            f.write("}\n\n\n")
            f.write("if test \"$Action\" = \"cam_res\" ; then\n")
            f.write("\t\tcam_down\n")
            f.write("\t\tcam_up\n")
            f.write("elif test \"$Action\" = \"cam_down\" ; then\n")
            f.write("\t\tcam_down\n")
            f.write("elif test \"$Action\" = \"cam_up\" ; then\n")
            f.write("\t\tcam_up\n")
            f.write("else\n")
            f.write("\t\tcam_handle\n")
            f.write("fi\n\n\n")
            f.write("exit 0\n")
            f.close()
            ca6 = "chmod 755 /usr/script/cam/%s.sh" % (self.camtoinstall)
            os.system(ca6)
            self.session.open(MessageBox, _("Camd has been installed!"), type = MessageBox.TYPE_INFO,timeout = 5)


    def skipCamInstall(self,reason):
        self.session.open(MessageBox,_("Camd install was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


    def getCamdList(self):
        camtoinstall = []
	try:
            for kitfile in os.listdir('/tmp/camdinstall'):
                camtoinstall.append((kitfile, '%s' % kitfile))

            return camtoinstall
        except:
            return camtoinstall   	

    def getCamaddList(self):
        camtoadd = []
        try: 
            for kitifile in os.listdir('/usr/script/cam'):
                camtoadd.append((kitifile, '%s' % kitifile))

            return camtoadd
        except:
            return camtoadd 


class CamdUninstall(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.askForCamdUninstall,ChoiceBox,_("Select Camd to uninstall!"),self.getCamdUnlist())

    def askForCamdUninstall(self,camtouninstall):
        if camtouninstall is None:
            self.skipCamUninstall(_("No Camd selected"))
        else:
            self.camtouninstall=camtouninstall[1]
            self.session.openWithCallback(self.UserScriptUninstall,MessageBox,_("remove %s?") % self.camtouninstall,MessageBox.TYPE_YESNO)
            
    def UserScriptUninstall(self,answer):
        if answer is None:
            self.skipCamUninstall(_("answer is None"))
        if answer is False:
            self.skipCamuninstall(_("you were not confirming"))
        else:
            cmd = "rm /usr/bin/cam/%s && rm /usr/script/cam/%s*"  % (self.camtouninstall, self.camtouninstall)
            os.system(cmd)
            self.session.open(MessageBox, _("Camd has been uninstalled!"), type = MessageBox.TYPE_INFO,timeout = 5)


    def skipCamUninstall(self,reason):
        self.session.open(MessageBox,_("Camd uninstall was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


    def getCamdUnlist(self):
        camtouninstall = []
        for kitfile in os.listdir("/usr/bin/cam"):
              camtouninstall.append(( kitfile, "%s" % kitfile ))
        return camtouninstall


class DialogOscamInstall(Screen):

	skin = """
		<screen name="DialogOscamInstall" position="60,245" size="600,10" title="PowerboardCamAdd">
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
offset = 60
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
		self.list = [ (_("Install standalone"), 0), (_("Add oscam to other cam"), 1) ]
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
###########################################################################
