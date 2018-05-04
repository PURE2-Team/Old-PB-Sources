#'''
#Created on 2013-03-16
#
#@author: delfi
#Edited by Franc 25.05.2016 / 12.11.2016
#'''
#Edited by Terra 06.12.2016 /31.12.2016
#'''
##########################################################
# -*- coding: utf-8 -*-

Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
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
from Components.Network import iNetwork

#from Screens.Console import Console
import os
import gettext
import sys
from Plugins.Extensions.PowerboardCenter.PBCon import PBConsole2

netinfo_script = '/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/netinfo_script.sh'



#************************************************************************************************************************************** 
import sys
from Tools.LoadPixmap import LoadPixmap
from Components.Sources.List import List
from Components.Button import Button
#************************************************************************************************************************************** 


class PBnetinfo(Screen):
    skin = """<screen name="PBnetinfo" position="center,center" size="800,600" title="PBnetinfo" flags="wfNoBorder">
        <ePixmap position="0,0" zPosition="-10" size="800,600" pixmap="OneKeyBlue/menu/menubg.png" />
        <widget name="menu" position="24,84" size="410,450" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" selectionPixmap="OneKeyBlue/selpic/listselection.png" />            
        <eLabel text="Powerboard Net Info" position="40,11" size="700,50" font="Regular;34" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" /> 
        <widget source="global.CurrentTime" render="Label" position="580,20" size="100,28" font="Regular;23" halign="right" backgroundColor="black" foregroundColor="grey" shadowOffset="-2,-2" shadowColor="black" transparent="1">
        <convert type="ClockToText">Format:%d.%b</convert>
        </widget>
        <widget source="global.CurrentTime" render="Label" position="690,20" size="80,28" font="Regular;23" halign="right" backgroundColor="black" shadowOffset="-2,-2" shadowColor="black" transparent="1">
        <convert type="ClockToText">Default</convert> 
        </widget>
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb.png" position="485,100" size="250,250" backgroundColor="black" alphatest="blend" />
        </screen>"""


    def __init__(self, session):
        skin = '%s/Skins/PBnetinfo.xml' % os.path.dirname(sys.modules[__name__].__file__)
        if os.path.exists(skin):
            f = open(skin, 'r')
            self.skin = f.read()
            f.close()
        else:
            self.skin = PBnetinfo.skin

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
            l.append(self.buildListEntry(_("TCP Connections"), _("TCP Connections"), "net.png"))
            l.append(self.buildListEntry(_("General Info"), _("General info about network. Please be patient!"), "net.png"))
            l.append(self.buildListEntry(_("Speed Info"), _("Test your internet speed. Please be patient!"), "net.png"))
            l.append(self.buildListEntry(_("Restart Network"), _("Restart your Network!"), "net.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
        else:
            est = False
            list = []
            list.append(SimpleEntry(_('TCP Connections'), 'tcpinfo.png'))
            list.append(SimpleEntry(_('General Info'), 'netspeed.png'))
            list.append(SimpleEntry(_('Speed Info'), 'net3.png'))
            list.append(SimpleEntry(_('Restart Network'), 'net.png'))
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
        if index == 0:
            self.session.open(PBConsole2, _('TCP Connections'), ['%s %s' % (netinfo_script, 'tcpinfo')])
        elif index == 1:
            self.session.open(PBConsole2, _('General Network Info'), ['%s %s' % (netinfo_script, 'general')])
        elif index == 2:
            self.session.open(PBConsole2, _('Speed Info'), ['%s %s' % (netinfo_script, 'speed')])
        elif index == 3:
            self.session.open(PBRestartNetwork)

    def quit(self):
        self.close()

def SimpleEntry(name, picture):
    res = [(name, picture)]
    picture = '/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/' + picture
    if name == '---':
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
                if element[0] == '---':
                    isDiv = True
                    if self.getSelectionIndex() < self.last:
                        self.up()
                    else:
                        self.down()

        except Exception as e:
            pass

        self.last = self.getSelectionIndex()
        if not isDiv:
            for f in self.onSelectionChanged:
                f()
                
######################################################################################################################################

class PBRestartNetwork(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        skin = """
            <screen name="RestartNetwork" position="center,center" size="600,100" title="Restart Network Adapter">
            <widget name="label" position="10,30" size="500,50" halign="center" font="Regular;20" transparent="1" foregroundColor="white" />
            </screen> """
        self.skin = skin
        self["label"] = Label(_("Please wait while your network is restarting..."))
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.restartLan)

    def setWindowTitle(self):
        self.setTitle(_("Restart Network Adapter"))

    def restartLan(self):
        iNetwork.restartNetwork(self.restartLanDataAvail)
  
    def restartLanDataAvail(self, data):
        if data is True:
            iNetwork.getInterfaces(self.getInterfacesDataAvail)

    def getInterfacesDataAvail(self, data):
		self.close()

