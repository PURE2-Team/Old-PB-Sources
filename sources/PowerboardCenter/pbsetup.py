#'''
#Created on 27.08.2011
#Edited by terrajoe 27.08.2016
#Edited by Franc 25.05.2016 / 12.11.2016
#@author: terrajoe
# -*- coding: utf-8 -*-

Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Plugins.Extensions.PowerboardCenter.PBCon import PBConsole2
from enigma import *
from boxbranding import getBoxType
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists, resolveFilename, SCOPE_ACTIVE_SKIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Sources.StaticText import StaticText

from Screens.InputBox import InputBox
from Screens.SkinSelector import *
from Screens.ChoiceBox import ChoiceBox
from Components.Input import Input
from Components.Label import Label
from Components.Pixmap import Pixmap, MovingPixmap
import os
import gettext


#************************************************************************************************************************************** 
import sys
from Tools.LoadPixmap import LoadPixmap
from Components.Sources.List import List
from Components.Button import Button
#************************************************************************************************************************************** 



class PBSetup(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 1280:
        skin = """
            <screen name="PBSetup" position="center,center" size="800,600" title="PowerboardSystemSetup">
            <widget name="menu" position="50,84" size="450,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardSystemSetup" position="40,11" size="700,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
            <screen name="PBSetup" position="center,center" size="650,500" title="PowerboardSystemSetup">
            <widget name="menu" position="50,84" size="370,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardSystemSetup" position="40,11" size="420,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
            <screen name="PBSetup" position="center,center" size="600,480" title="PowerboardSystemSetup">
            <widget name="menu" position="50,84" size="370,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardSystemSetup" position="40,11" size="420,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
        
        self.labelmount = "0"
        if os.path.isfile("/etc/enigma2/.labelmount"):
            self.labelmount = "1"
        else:
            self.labelmount = "0"
        
        # list = []
        # list.append(SimpleEntry(_("Satfind"), "system.png"))
        # list.append(SimpleEntry(_("Auto Systemupdate"), "system.png"))
        # if self.labelmount == "0":
            # list.append(SimpleEntry(_("PB Device Manager"), "system.png"))
        # else:
            # list.append(SimpleEntry(_("PB Label Mounting"), "system.png"))
# #        list.append(SimpleEntry(_("PB-SetEPG-Path"), "system.png"))
        # list.append(SimpleEntry(_("PB Set Picon Path"), "system.png"))
        # list.append(SimpleEntry(_("Delete plugins and/or crashlogs"), "system.png"))
        # list.append(SimpleEntry(_("Camd Installer-Uninstaller"), "system.png"))
        # list.append(SimpleEntry(_("PB Expert Installer"), "system.png"))
        # list.append(SimpleEntry(_("Script Starter"), "system.png"))
        # list.append(SimpleEntry(_("Auto Cam Restarter"), "system.png"))
        # if os.path.isfile("/usr/share/enigma2/display/skin_display.xml"):
            # list.append(SimpleEntry(_("LCD Skin Selector"), "system.png"))

        # self['menu'] = ExtrasList(list)
		
		
		
        global est
        est = False
		
		
		
#************************************************************************************************************************************** 
	    # Estuary - Start Here	
        self["page"] = Label()
        self["page"].setText(" ")
		
		
        

        if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
            est = True
            l = []
            l.append(self.buildListEntry(_("Satfind"), _("Check your signals"), "scan.png"))
            l.append(self.buildListEntry(_("Auto Systemupdate"), _("Configure how and when system can make update"), "pbnigma.png"))
            if self.labelmount == "0":
                l.append(self.buildListEntry(_("PB Device Manager"), _("Mounts tools)"), "hdd.png"))
            else:
                l.append(self.buildListEntry(_("PB Label Mounting"), _("Mounts tools"), "hdd.png"))
            #l.append(self.buildListEntry(_("PB SetEPG Path"), _("Read the fresh daily news from our board, stay tune always"), "pbnews.png"))
            l.append(self.buildListEntry(_("PB Set Picon Path"), _("Change picon path"), "syssetup.png"))
            l.append(self.buildListEntry(_("Delete plugins and/or crashlogs/debuglogs"), _("Clear your box from old logs/debugs"), "stop.png"))
            l.append(self.buildListEntry(_("Camd Installer-Uninstaller"), _("Install/Uninstall Camd"), "camman.png"))
            l.append(self.buildListEntry(_("PB Expert Installer"), _("Install additional plugins/extensions/drivers..."), "sysinfo.png"))
            l.append(self.buildListEntry(_("Script Starter"), _("Run your script when you want"), "search.png"))
            l.append(self.buildListEntry(_("Auto Cam Restarter"), _("Choose time/date to restart your cam"), "camman.png"))
			
            if os.path.isfile("/usr/share/enigma2/display/skin_display.xml"):
                l.append(self.buildListEntry(_("LCD Skin Selector"), _("Choose LCD skin"), "gui.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
			
        else:
            est = False
            list = []
            list.append(SimpleEntry(_("Satfind"), "system.png"))
            list.append(SimpleEntry(_("Auto Systemupdate"), "system.png"))
            if self.labelmount == "0":
                list.append(SimpleEntry(_("PB Device Manager"), "system.png"))
            else:
                list.append(SimpleEntry(_("PB Label Mounting"), "system.png"))
# #        list.append(SimpleEntry(_("PB-SetEPG-Path"), "system.png"))
            list.append(SimpleEntry(_("PB Set Picon Path"), "system.png"))
            list.append(SimpleEntry(_("Delete plugins and/or crashlogs/debuglogs"), "system.png"))
            list.append(SimpleEntry(_("Camd Installer-Uninstaller"), "system.png"))
            list.append(SimpleEntry(_("PB Expert Installer"), "system.png"))
            list.append(SimpleEntry(_("Script Starter"), "system.png"))
            list.append(SimpleEntry(_("Auto Cam Restarter"), "system.png"))
            if os.path.isfile("/usr/share/enigma2/display/skin_display.xml"):
                list.append(SimpleEntry(_("LCD Skin Selector"), "system.png"))

            self['menu'] = ExtrasList(list)
			
#************************************************************************************************************************************** 
		
		
		
		
		
		
        self["actions"] = ActionMap(["SetupActions", "OkCancelActions", "ColorActions", "DirectionActions"],
        {
            "red": self.quit,
            "ok": self.ok,
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
        
		
		
		

                
    def ok(self):
        if est == True:
            index = self['list'].getSelectedIndex()
        else:
            index = self['menu'].getSelectedIndex()
			
        if (index == 0):
            try:
                from Plugins.SystemPlugins.Satfinder.plugin import Satfinder
            except Exception, e:
                print e
                return
                
            self.session.open(Satfinder)
        elif (index == 1):
            try:
                from Plugins.Extensions.PowerboardCenter.pbupdate import PBUpdate
            except Exception, e:
                print e
                return
                
            self.session.open(PBUpdate)
            
        elif (index == 2) and self.labelmount == "0":
            try:
                from Plugins.Extensions.PowerboardCenter.PBDeviceManager import HddSetup
            except Exception, e:
                print e
                return
                
            self.session.open(HddSetup)
        
        elif (index == 2) and self.labelmount == "1":
            try:
                from Plugins.Extensions.PowerboardCenter.PBExpander import Expander
            except Exception, e:
                print e
                return
                
            self.session.open(Expander)
#        elif (index == 3):
#            try:
#                from Plugins.SystemPlugins.EPGPathSet.plugin import SetEPGPath
#            except Exception, e:
#                print e
#                return
#                
#            self.session.open(SetEPGPath)
        elif (index == 3):
            try:
                from Plugins.SystemPlugins.PBPiconPathSet.plugin import SetPiconPath
            except Exception, e:
                print e
                return
                
            self.session.open(SetPiconPath)
            
        elif (index == 4):
            try:
                from Plugins.Extensions.PowerboardCenter.pbremover import PBRemover
            except Exception, e:
                print e
                return
                
            self.session.open(PBRemover)
        elif (index == 5):
            try:
                from Plugins.Extensions.PowerboardCenter.pbcamdinstaller import PBCamdinstaller
            except Exception, e:
                print e
                return
                
            self.session.open(PBCamdinstaller)
        elif (index == 6):
            try:
                from Plugins.Extensions.PowerboardCenter.addonexpert import PowerboardExpertInstaller
            except Exception, e:
                print e
                return
                
            self.session.open(PowerboardExpertInstaller)
        elif (index == 7):
            try:
                from Plugins.Extensions.PowerboardCenter.pbscriptstarter import UserScript
            except Exception, e:
                print e
                return
                
            self.session.open(UserScript)

        elif (index == 8):
            try:
                from Plugins.Extensions.PowerboardCenter.pbcamrestart import PBCamRestart
            except Exception, e:
                print e
                return
                
            self.session.open(PBCamRestart)

        elif (index == 9):

            self.session.open(LcdSkinSelector)
            
    def quit(self):
        self.close()
        
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
