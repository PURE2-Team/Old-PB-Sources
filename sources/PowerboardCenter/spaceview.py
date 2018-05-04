#'''
#Created on 2013-06-27
#
#@author: stibbich <stibbich@pb-powerboard.com>
#'''
#Edited by Franc 25.05.2016 and 09.03.2017
##########################################################
# -*- coding: utf-8 -*-

Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from enigma import *
from Screens.Screen import Screen
from Components.ConfigList import *
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.MenuList import MenuList
from Components.Input import Input
from Components.Label import Label
from Components.Button import Button
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent

from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.Directories import fileExists, resolveFilename, SCOPE_ACTIVE_SKIN
import os
import gettext

           
class PBSpaceview(Screen):
    skin = """
        <screen name="PBSpaceview" position="center,center" size="850,420" title="PB-Space-Viewer" flags="wfNoBorder">
            <widget name="menu" position="45,74" size="650,300" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="PB Space Viewer" position="20,8" size="485,50" font="Regular;28" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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

        list = []
        
        list.append(SimpleEntry(_("flash"), "root", "sysinfo.png"))

        mounts = open("/proc/mounts", "r")
        for line in mounts:
            if "media/" in line:
                iliste = line.split(" ")
                inliste = iliste[1]
                list.append(SimpleEntry(_("%s") % inliste, inliste, "sysinfo.png"))
        mounts.close()
        

        Screen.__init__(self, session)
        self['menu'] = ExtrasList(list)
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
            "ok": self.go,
            "cancel": self.cancel
        }, -1)

    def go(self):
        mount = self["menu"].l.getCurrentSelection()
        print "mount", mount
        a = mount[0]
        print "a", a
        self.session.open(SView, a[1])

    def cancel(self):
        print "\n[menu] cancel\n"
        self.close(None)


class SView(ConfigListScreen, Screen):
    def __init__(self, session, device):
        self.skin = """
            <screen name="SView" position="center,center" size="600,400" title="Spaceview">
                <widget font="Regular;18" halign="center" name="Size" position="0,10" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="Used" position="0,40" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="Available" position="0,70" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="Use in %" position="0,100" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="Partition" position="0,130" size="500,25" valign="center" />
                <ePixmap position="70,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/red_button.png" transparent="1" alphatest="on" />
                <ePixmap position="350,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/green_button.png" transparent="1" alphatest="on" />
                <widget name="key_red" position="70,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green" position="350,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
            </screen>"""
        Screen.__init__(self, session)
        self.device = device
        self.list = []

        ConfigListScreen.__init__(self, self.list)

        self["key_green"] = Button("OK")
        self["key_red"] = Button(_("Exit"))
        self["Size"] = Label("Size: unknow")
        self["Used"] = Label("Used: unknow")
        self["Available"] = Label("Available: unknow")
        self["Use in %"] = Label("Use: unknow")
        self["Partition"] = Label("Partition: unknow")
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "red": self.keyCancel,
            "green": self.keyCancel,
            "cancel": self.keyCancel,
        }, -2)

        self.onLayoutFinish.append(self.drawInfo)

    def drawInfo(self):
        try:
            sizeread = os.popen("df -h | grep %s | tr -s ' '" % self.device)
            c = sizeread.read().strip().split(" ")
            self["Size"].setText("Size: %s" % c[1])
            self["Used"].setText("Used: %s" % c[2])
            self["Available"].setText("Available: %s" % c[3])
            self["Use in %"].setText("Use: %s" % c[4])
            self["Partition"].setText("Partition: %s" % c[0])
            sizeread.close()
        except Exception, e:
            pass


###########################################################################
def SimpleEntry(name, dev, picture):
    res = [(name, dev, picture)]
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
