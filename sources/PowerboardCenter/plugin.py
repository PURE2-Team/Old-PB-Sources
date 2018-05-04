##'''
#Created on 03.10.2011
#
#Edited by terrajoe 27.08.2016 / 26.12.2016
#Edited by Franc 25.05.2016 / 12.11.2016
#
#@author: terrajoe
# -*- coding: utf-8 -*-



VersionPB = "v7.0.0"
Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from enigma import *
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists, resolveFilename, SCOPE_ACTIVE_SKIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Plugins.Plugin import PluginDescriptor
from Components.Sources.StaticText import StaticText
import os



#************************************************************************************************************************************** 
import sys
from Tools.LoadPixmap import LoadPixmap
from Components.Sources.List import List
from Components.Button import Button
from os import popen, statvfs, path
from Components.Label import Label
from Screens.SoftwareUpdate import UpdatePlugin
#************************************************************************************************************************************** 

###########################################################################

def Check_Softcam():
	found = False
	try:
		for x in os.listdir('/usr/script/cam'):
			if x.find('.sh') > -1:
				found = True
				break;
		return found
	except Exception, e:
		print e
		return

###########################################################################

def main(session,**kwargs):
    session.open(powerboardCenter)
  
###########################################################################
      
def Plugins(path,**kwargs):
    global plugin_path
    plugin_path = path
    return [PluginDescriptor(name="Powerboard-Center", description=_("Powerboard-Panel"), where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU ], icon="powerboard.png", fnc=main)]

###########################################################################

class powerboardCenter(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 1280:
        skin = """
            <screen name="powerboardCenter" position="center,center" size="800,600" title="PowerboardCenter">
            <widget name="menu" position="50,84" size="450,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardCenter" position="40,11" size="700,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
            <widget source="VersionPB" render="Label" position="725,545" size="75,25" font="Regular;11" shadowOffset="-3,-3" shadowColor="black" backgroundColor="black" transparent="1" />
            <widget source="global.CurrentTime" render="Label" position="580,20" size="100,28" font="Regular;23" halign="right" backgroundColor="black" foregroundColor="grey" shadowOffset="-2,-2" shadowColor="black" transparent="1">
                <convert type="ClockToText">Format:%d.%b</convert>
            </widget>
            <widget source="global.CurrentTime" render="Label" position="690,20" size="80,28" font="Regular;23" halign="right" backgroundColor="black" shadowOffset="-2,-2" shadowColor="black" transparent="1">
                <convert type="ClockToText">Default</convert>
            </widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb.png" position="528,center" size="250,250" backgroundColor="black" alphatest="blend" />
            </screen>"""
    elif sz_w == 1024:
        skin = """
            <screen name="powerboardCenter" position="center,center" size="650,500" title="PowerboardCenter">
            <widget name="menu" position="50,84" size="370,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardCenter" position="40,11" size="420,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
            <widget source="VersionPB" render="Label" position="600,450" size="75,25" font="Regular;11" shadowOffset="-3,-3" shadowColor="black" backgroundColor="black" transparent="1" />
            <widget source="global.CurrentTime" render="Label" position="460,20" size="100,28" font="Regular;23" halign="right" backgroundColor="black" foregroundColor="grey" shadowOffset="-2,-2" shadowColor="black" transparent="1">
                <convert type="ClockToText">Format:%d.%b</convert>
            </widget>
            <widget source="global.CurrentTime" render="Label" position="560,20" size="80,28" font="Regular;23" halign="right" backgroundColor="black" shadowOffset="-2,-2" shadowColor="black" transparent="1">
                <convert type="ClockToText">Default</convert>
            </widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb.png" position="460,center" size="180,180" backgroundColor="black" alphatest="blend" />
            </screen>"""
    else:
        skin = """
            <screen name="powerboardCenter" position="center,center" size="600,480" title="PowerboardCenter">
            <widget name="menu" position="50,84" size="370,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardCenter" position="40,11" size="420,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
            <widget source="VersionPB" render="Label" position="550,450" size="75,25" font="Regular;11" shadowOffset="-3,-3" shadowColor="black" backgroundColor="black" transparent="1" />
            <widget source="global.CurrentTime" render="Label" position="400,20" size="100,28" font="Regular;23" halign="right" backgroundColor="black" foregroundColor="grey" shadowOffset="-2,-2" shadowColor="black" transparent="1">
                <convert type="ClockToText">Format:%d.%b</convert>
            </widget>
            <widget source="global.CurrentTime" render="Label" position="490,20" size="80,28" font="Regular;23" halign="right" backgroundColor="black" shadowOffset="-2,-2" shadowColor="black" transparent="1">
                <convert type="ClockToText">Default</convert>
            </widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb_small.png" position="400,center" size="180,180" backgroundColor="black" alphatest="blend" />
            </screen>"""


    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        self.session = session
        
		
        global est
        est = False
		
		
#************************************************************************************************************************************** 
	    # Estuary - Start Here	
        self["page"] = Label()
        self["page"].setText(" ")
		
		
        

        if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
            est = True
            l = []
            l.append(self.buildListEntry(_("Software Manager"), _("Everything about software: Backup/Restore/Update..."), "addon.png"))
            if Check_Softcam() is True:
                l.append(self.buildListEntry(_("Cam Manager"), _("Camd/EMU Control"), "camman.png"))
            else:
                l.append(self.buildListEntry(_("Wildcard"), _("Wildcard Control"), "syssetup.png"))
            l.append(self.buildListEntry(_("PB Newsreader"), _("Read the fresh daily news from our board, always stay tune"), "pbnews.png"))
            l.append(self.buildListEntry(_("Powerboard System Setup"), _("Make your image smartest with a lot of additional settings"), "syssetup.png"))
            l.append(self.buildListEntry(_("Powerboard System Settings"), _("Some system settings"), "syssetup.png"))
            l.append(self.buildListEntry(_("Powerboard System Info"), _("Get info of everything you want to know about your box"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Powerboard Design"), _("Change GUI elements at your will"), "gui.png"))
            l.append(self.buildListEntry(_("Team Info"), _("Our proudly team"), "info.png"))
#            l.append(self.buildListEntry(_("Internet radio"), _("Listen the online radio"), "radio-icon.png"))
            l.append(self.buildListEntry("---", _(" "), "div_small.png"))
            l.append(self.buildListEntry(_("Restart GUI"), _("Restart enigma2 from this point"), "reboot.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
            self["VersionPB"] = StaticText("Powerboad Center " + str(VersionPB))
			
        else:
            est = False
            list = []
            list.append(SimpleEntry(_("Softwaremanager"), "addon.png"))
            if Check_Softcam() is True:
                list.append(SimpleEntry(_("Cam Manager"), "camman.png"))
            else:
                list.append(SimpleEntry(_("Wildcard"), "syssetup.png"))
            list.append(SimpleEntry(_("PB-Newsreader"), "pbnews.png"))
            list.append(SimpleEntry(_("Powerboard-System-Setup"), "syssetup.png"))
            list.append(SimpleEntry(_("Powerboard-System-Settings"), "syssetup.png"))
            list.append(SimpleEntry(_("Powerboard-System-Info"), "sysinfo.png"))
            list.append(SimpleEntry(_("Powerboard-Design"), "system.png"))
            list.append(SimpleEntry(_("Team-Info"), "info.png"))
#            list.append(SimpleEntry(_("Internetradio"), "radio-icon.png"))
            list.append(SimpleEntry("---", "div_small.png"))
            list.append(SimpleEntry(_("Restart GUI"), "reboot.png"))
            self['menu'] = ExtrasList(list)
			
            self["VersionPB"] = StaticText(VersionPB)
			
#************************************************************************************************************************************** 
		




 
		####################################################################################################
		#Buttons Akcije
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
                {
                    "red": self.quit,
                    "green": self.checkupdate,
                    #"yellow": self.about,
                    "blue": self.about,
                    "cancel": self.quit,
                    #"up": self.keyUp,
                    #"down": self.keyDown,
                    "ok": self.ok,
                }, -2)
		
        #Postavi caption na color gumbe
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button(_("Check for update"))
        #self["key_yellow"] = Button("About")
        self["key_blue"] = Button(_("About"))
		#################################################################################################### 
 
 
 
 
 
 
 
 
 

#************************************************************************************************************************************** 
		# Estuary - Start Here	
    def buildListEntry(self, title, description, image):
        pixmap = LoadPixmap(cached=True, path="%s/pics/fhd/%s" % (os.path.dirname(sys.modules[__name__].__file__), image));
        return((pixmap, title, description))	
#************************************************************************************************************************************** 
		
		
    # def keyUp(self):
        # print "alooooooooooo ", self['list'].getSelectedIndex()
        # self["list"].up()


    # def keyDown(self):
        # print "alooooooooooo ", self['list'].getSelectedIndex()
        # self["list"].down()

		
                
    def ok(self):
        if est == True:
            index = self['list'].getSelectedIndex()
        else:
            index = self['menu'].getSelectedIndex()
			
        if (index == 0):
            try:
                from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePluginMenu
            except Exception, e:
                print e
                return
                
            self.session.open(UpdatePluginMenu)
        elif (index == 1) and Check_Softcam() is True:
            try:
                from Plugins.Extensions.DreamCC.plugin import DreamCC
            except Exception, e:
                print e
                return
                
            self.session.open(DreamCC)
        elif (index == 2):
            try:
                from Plugins.Extensions.PowerboardCenter.newsreader import FeedScreenList
            except Exception, e:
                print e
                return
                
            self.session.open(FeedScreenList)
        elif (index == 3):
            try:
                from Plugins.Extensions.PowerboardCenter.pbsetup import PBSetup
            except Exception, e:
                print e
                return
                
            self.session.open(PBSetup)
        elif (index == 4):
            try:
                from Plugins.Extensions.PowerboardCenter.PBConfigs import PowerboardSetup
            except Exception, e:
                print e
                return
                
            self.session.open(PowerboardSetup)
        elif (index == 5):
            try:
                from Plugins.Extensions.PowerboardCenter.info import PBInfo
            except Exception, e:
                print e
                return
                
            self.session.open(PBInfo)
        elif (index == 6):
            try:
                from Plugins.Extensions.PowerboardCenter.pbdesign import PBDesign
            except Exception, e:
                print e
                return
                
            self.session.open(PBDesign)
        elif (index == 7):
            try:
                from Plugins.Extensions.PowerboardCenter.pbabout import PBAboutTeam
            except Exception, e:
                print e
                return
                
            self.session.open(PBAboutTeam)
#        elif (index == 8):
#            try:
#                from Plugins.Extensions.PowerboardCenter.pbradio import PBRadio
#            except Exception, e:
#                print e
#                return
#                
#            self.session.open(PBRadio)
        elif (index == 9):
            from Screens.Standby import TryQuitMainloop
            self.session.open(TryQuitMainloop, 3)
        
    def quit(self):
        self.close()
		
		
    def about(self):
        try:
            from Screens.About import About
        except Exception, e:
             print e
             return
        self.session.open(About)
		
    def checkupdate(self):
        try:
            self.session.open(UpdatePlugin) 
        except Exception, e:
           print e
           return
        
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
        res.append(MultiContentEntryText(pos=(60, 5), size=(450, 38), font=0, text=name))
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

