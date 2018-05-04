#'''
#Created on 27.08.2011
#
#@author: terrajoe
#Edited by Franc 25.05.2016 / 12.11.2016
# -*- coding: utf-8 -*-

Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Plugins.Extensions.PowerboardCenter.PBCon import PBConsole2
from enigma import *
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists, resolveFilename, SCOPE_ACTIVE_SKIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest


from Screens.InputBox import InputBox
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
from os import system, path
#************************************************************************************************************************************** 





class PBInfo(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 1280:
        skin = """
            <screen name="PBInfo" position="center,center" size="800,600" title="PowerboardSystemInfo">
            <widget name="menu" position="50,84" size="450,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardSystemInfo" position="40,11" size="700,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
            <screen name="PBInfo" position="center,center" size="650,500" title="PowerboardSystemInfo">
            <widget name="menu" position="50,84" size="370,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardSystemInfo" position="40,11" size="420,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
            <screen name="PBInfo" position="center,center" size="600,480" title="PowerboardSystemInfo">
            <widget name="menu" position="50,84" size="370,388" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PowerboardSystemInfo" position="40,11" size="420,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
            l.append(self.buildListEntry(_("Memory"), _("Memory"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Process"), _("Process"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Show Mounts"), _("Show Mounts"), "sysinfo.png"))
            l.append(self.buildListEntry(_("CPU Info"), _("CPU Info"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Crypt Info"), _("Crypt Info"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Spaceview"), _("Spaceview"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Kernel Messages"), _("Kernel Messages"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Device Performance"), _("Device Performance"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Loaded Modules"), _("Loaded Modules"), "sysinfo.png"))
            l.append(self.buildListEntry(_("Netinfo"), _("WNetinfo"), "sysinfo.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
        else:
            est = False
            list = []
            list.append(SimpleEntry(_("Memory"), "systeminfo.png"))
            list.append(SimpleEntry(_("Prozesse"), "systeminfo.png"))
            list.append(SimpleEntry(_("Show Mounts"), "systeminfo.png"))
            list.append(SimpleEntry(_("CPU-Info"), "systeminfo.png"))
            list.append(SimpleEntry(_("Crypt-Info"), "systeminfo.png"))
            list.append(SimpleEntry(_("Spaceview"), "systeminfo.png"))
            list.append(SimpleEntry(_("Kernel Messages"), "systeminfo.png"))
            list.append(SimpleEntry(_("Device Performance"), "systeminfo.png"))
            list.append(SimpleEntry(_("Loaded Modules"), "systeminfo.png"))
            list.append(SimpleEntry(_("Netinfo"), "systeminfo.png"))
            self['menu'] = ExtrasList(list)
			
#************************************************************************************************************************************** 				
				
				
				
	
				

		
        self["actions"] = ActionMap(["SetupActions", "OkCancelActions", "ColorActions", "DirectionActions"],
        {
            "red": self.quit,
            "ok": self.ok,
            "cancel": self.quit,
            "green": self.clearmem
        }, -2)
		
		
 #************************************************************************************************************************************** 
		# Estuary - Start Here	
        #Postavi caption na color gumbe
        self["key_red"] = Button(_("Back"))
        self["key_green"] = Button(_("Clear Cache"))

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
            self.session.open(PBConsole2,_("Memory"),["free"])
        elif (index == 1):
            self.session.open(PBConsole2,_("Prozesse"),["ps"])

        elif (index == 2):
            self.session.open(PBConsole2,_("Show Mounts"),["mount"])
        elif (index == 3):
            self.session.open(PBConsole2,_("CPU-Info"),["cat /proc/cpuinfo | egrep 'system|build|processor|cpu model|Bogo|tlb|ASE'"])
        elif (index == 4):
            self.session.open(PBConsole2,_("Crypt-Info"), ["test -e /tmp/ecm.info && cat /tmp/ecm.info || echo 'FTA or cannot decode'"])
        elif (index == 5):
            try:
                from Plugins.Extensions.PowerboardCenter.spaceview import PBSpaceview
            except Exception, e:
                print e
                return
                
            self.session.open(PBSpaceview)
        elif (index == 6):
            self.session.open(PBConsole2,_("Kernel Messages"),["dmesg"])
        elif (index == 7):
            DevPerf(self.session)
        elif (index == 8):
            self.session.open(PBConsole2,_("Loaded Modules"),["lsmod"])
        elif (index == 9):
            try:
                from Plugins.Extensions.PowerboardCenter.PBnetinfo import PBnetinfo
            except Exception, e:
                print e
                return
                
            self.session.open(PBnetinfo)
            
    def quit(self):
        self.close()


    def clearmem(self):
        before = self.getRAMfree()
        try:
            system("sync")
            print "*** PB Memory Clear *** - sync is on"
            system("echo 3 > /proc/sys/vm/drop_caches")
            after = self.getRAMfree()
            save = int(after) - int(before)
            self.session.open(MessageBox,_('Finished: \n Free memory before cleaning: ' + before + ' MB \n Free memory after cleaning: ' + after + ' MB \n You save: ' + str(save) + ' MB'), MessageBox.TYPE_INFO, timeout = 20)
        except Exception, e:
            print e
		
		
		
    #MEMORIJA START
    #Za citanje memorije u telnet upises:  cat /proc/meminfo - izlistat ce se sva moguca memorija, tipa:
    # MemTotal:         506424 kB
    # MemFree:          179412 kB
    # MemAvailable:     404468 kB
    # itd...

    #Onda samo u kod upises, zavisno koju memoriju hoces citati:
    #if lisp[0] == "MemAvailable:":
    #za MemFree
    #if lisp[0] == "MemFree:":
    #itd...
	
		
    def getRAMfree(self):
        info = ""
        if path.exists('/proc/meminfo'):
            f = open('/proc/meminfo', 'r')
            temp = f.readlines()
            f.close()
            try:
                for lines in temp:
                    lisp = lines.split()
                    if lisp[0] == "MemFree:":
                        #info = "RAM-Free: " + str(int(lisp[1]) / 1024) + " MB"
                        info = str(int(lisp[1]) / 1024) #+ " MB"
                        break
            except:
                pass
        return info
		
        
#################################################################################

class DevPerf(Screen):
    def __init__(self, session):
        self.session = session
        devlist = self.GetDeviceList()
        if devlist == []:
            self.session.open(MessageBox,_("no device connected"), MessageBox.TYPE_ERROR)
        else:
            liste = list(set(devlist))
            self.session.openWithCallback(self.AskForDevice,ChoiceBox,_("Select device please!"),liste)

    def AskForDevice(self,userkit):
        if userkit is None:
            self.SkipDevice(_("No device selected!"))
        else:
            self.userkit=userkit[1]
            self.session.openWithCallback(self.UserScriptInstall,MessageBox,_("test performance of %s ?") % self.userkit,MessageBox.TYPE_YESNO)
            
    def UserScriptInstall(self,answer):
        if answer is None:
            self.SkipDevice(_("answer is None"))
        if answer is False:
            self.SkipDevice(_("you were not confirming"))
        else:
            title = _("testing performance of %s" %(self.userkit))
            cmd = "hdparm -Tt %s"  % (self.userkit)
            self.session.open(PBConsole2,_(title),[cmd])
            
    def SkipDevice(self,reason):
        self.session.open(MessageBox,_("performancetest was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


    def GetDeviceList(self):
       userkits = []
       devs = os.popen("blkid", "r")
       for line in devs:
           if "ubifs" not in line:
               iliste = line.split(":")
               inliste = iliste[0]
               print inliste
               h = inliste[4:-1]
               g = inliste[:-1]
               if 'mmc' in inliste:
                   h = inliste[4:-2]
                   g = inliste
               print h
               print g
               dev = 'Unknown'
               try:
                   dev = open("/sys/block/%s/device/model" % h, "r").read().strip()
               except:
                   try:
                       dev = open('/sys/block/%s/device/name' % h, 'r').read().strip()
                   except:
                       pass

               userkits.append((g + '   ' + dev, '%s' % g))

       return userkits


#################################################################################
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
