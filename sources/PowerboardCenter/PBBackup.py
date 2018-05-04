#'''
#Created on 15.07.2011
#changed on 17.07.2011
#@author: terrajoe
#'''
##########################################################
# -*- coding: utf-8 -*-

from __init__ import _
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from enigma import *
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest

class PBBackup(Screen):
    skin = """
        <screen name="PBBackup" position="center,center" size="650,420" title="Backup / Restore Scripts" flags="wfNoBorder">
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

        list = []
        list.append(SimpleEntry(_("Setup Path for Backup"), "path.png"))
        list.append(SimpleEntry("---", "div.png"))
        list.append(SimpleEntry(_("Backup Keys"), "safe.png"))
        list.append(SimpleEntry(_("Backup Settings"), "safe.png"))
        list.append(SimpleEntry(_("Backup Cams and Configs"), "safe.png"))
        list.append(SimpleEntry(_("Backup Pluginlist"), "safe.png"))
        list.append(SimpleEntry(_("Backup all"), "safe.png"))
        list.append(SimpleEntry("---", "div.png"))
        list.append(SimpleEntry(_("Restore Keys"), "restore.png"))
        list.append(SimpleEntry(_("Restore Settings"), "restore.png"))
        list.append(SimpleEntry(_("Restore Cams and Configs"), "restore.png"))
        list.append(SimpleEntry(_("Restore Pluginlist with new Plugins"), "restore.png"))
        list.append(SimpleEntry(_("Restore all"), "restore.png"))
        list.append(SimpleEntry("---", "div.png"))
        list.append(SimpleEntry(_("Delete all Backups"), "trash.png"))

        Screen.__init__(self, session)
        self['menu'] = ExtrasList(list)
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
            "ok": self.go,
            "cancel": self.cancel
        }, -1)

    def go(self):
        index = self['menu'].getSelectedIndex()
        if (index == 0):
			try:
				from Plugins.Extensions.PowerboardCenter.backuppath import SetBackupPath
			except Exception, e:
				print e
				return
			self.session.open(SetBackupPath)
        elif (index == 2):
            self.session.open(Console,_("Backup Keys"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Backup_keys.sh")])
        elif (index == 3):
            self.session.open(Console,_("Backup Settings"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Backup_settings.sh")])
        elif (index == 4):
            self.session.open(Console,_("Backup Cams and Configs"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Backup_camsandconfigs.sh")])
        elif (index == 5):
            self.session.open(Console,_("Backup Pluginlist"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Backup_plugins.sh")])
        elif (index == 6):
            self.session.open(Console,_("Backup all"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Backup_all.sh")])
        elif (index == 8):
            self.session.open(Console,_("Restore Keys"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Restore_keys.sh")])
        elif (index == 9):
            self.session.open(Console,_("Restore Settings"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Restore_settings.sh")])
        elif (index == 10):
            self.session.open(Console,_("Restore Cams and Configs"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Restore_camsandconfigs.sh")])
        elif (index == 11):
            self.session.open(Console,_("Restore Pluginlist with new Plugins"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Restore_plugins.sh")])
        elif (index == 12):
            self.session.open(Console,_("Restore all"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Restore_all.sh")])
        elif (index == 14):
            self.session.open(Console,_("Delete all Backups"), cmdlist=[("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/Delete_all_backups.sh")])

    def cancel(self):
        print "\n[menu] cancel\n"
        self.close(None)

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
        res.append(MultiContentEntryText(pos=(60, 10), size=(450, 38), font=0, text=name))

    return res

class ExtrasList(MenuList, HTMLComponent, GUIComponent):
    def __init__(self, list, enableWrapAround = False):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.list = list
        self.l.setList(list)
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