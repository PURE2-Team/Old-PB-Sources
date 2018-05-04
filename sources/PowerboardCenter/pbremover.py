# 2012-01-20
#
#@author: stibbich <stibbich@pb-powerboard.com>
#
# 2014-09-28
#@Franc: added some exceptions for skin list
#Edited by Franc 25.05.2016 / 12.11.2016
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








class PBRemover(Screen):
    skin = """
        <screen name="PBRemover" position="center,center" size="650,420" title="PB Remove Tools" flags="wfNoBorder">
            <widget name="menu" position="45,84" size="425,300" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="Remove plugins and/or crashlogs" position="20,8" size="485,50" font="Regular;28" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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
            l.append(self.buildListEntry(_("Remove an extension plugin"), _("Please choose plugin to uninstall"), "stop.png"))
            l.append(self.buildListEntry(_("Remove a system plugin"), _("Please choose system plugin to uninstall"), "stop.png"))
            l.append(self.buildListEntry(_("Remove a skin"), _("Please choose skin to uninstall"), "stop.png"))
            l.append(self.buildListEntry("---", _(" "), "div_small.png"))
            l.append(self.buildListEntry(_("Remove crashlogs"), _("Remove old crashlogs/debuglogs"), "stop.png"))

            self["list"] = List(l)  
            self["page"].setText("Items: " + str(len(l)))
        else:
            est = False
            list = []
            list.append(SimpleEntry(_("Remove an extension-plugin"), "trash.png"))
            list.append(SimpleEntry(_("Remove a system-plugin"), "trash.png"))
            list.append(SimpleEntry(_("Remove a skin"), "trash.png"))
            list.append(SimpleEntry("      ", "div_small0.png"))
            list.append(SimpleEntry(_("Remove crashlogs"), "trash.png"))
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
        if est == True:
            index = self['list'].getSelectedIndex()
        else:
            index = self['menu'].getSelectedIndex()
        if (index == 0):
            ExtPluginRemove(self.session)
        elif (index == 1):
            SysPluginRemove(self.session)
        elif (index == 2):
            SkinRemove(self.session)
        elif (index == 4):
            CrashlogRemove(self.session)

    def cancel(self):
        print "\n[menu] cancel\n"
        self.close(None)
		
    def quit(self):
        self.close()


class ExtPluginRemove(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.askForExtPlugin,ChoiceBox,_("Select extension to remove!"),self.getExtUnlist())

    def askForExtPlugin(self,exttouninstall):
        if exttouninstall is None:
            self.skipExtUninstall(_("No extension selected"))
        else:
            self.exttouninstall=exttouninstall[1]
            self.session.openWithCallback(self.UserScriptUninstall,MessageBox,_("remove %s?") % self.exttouninstall,MessageBox.TYPE_YESNO)
            
    def UserScriptUninstall(self,answer):
        if answer is None:
            self.skipExtUninstall(_("answer is None"))
        if answer is False:
            self.skipExtUninstall(_("you were not confirming"))
        else:
            cmd = "rm -fr /usr/lib/enigma2/python/Plugins/Extensions/%s"  % (self.exttouninstall)
            os.system(cmd)
            self.session.open(MessageBox, _("Extension has been removed!"), type = MessageBox.TYPE_INFO,timeout = 5)


    def skipExtUninstall(self,reason):
        self.session.open(MessageBox,_("Remove of extension was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


    def getExtUnlist(self):
        exttouninstall = []
        for folder in os.listdir("/usr/lib/enigma2/python/Plugins/Extensions/"):
            if not folder.startswith("__init"):
                exttouninstall.append(( folder, "%s" % folder ))
        return exttouninstall

class SysPluginRemove(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.askForSysPlugin,ChoiceBox,_("Select systemplugin to remove!"),self.getSysUnlist())

    def askForSysPlugin(self,systouninstall):
        if systouninstall is None:
            self.skipSysUninstall(_("No systemplugin selected"))
        else:
            self.systouninstall=systouninstall[1]
            self.session.openWithCallback(self.UserScriptUninstall,MessageBox,_("remove %s?") % self.systouninstall,MessageBox.TYPE_YESNO)
            
    def UserScriptUninstall(self,answer):
        if answer is None:
            self.skipSysUninstall(_("answer is None"))
        if answer is False:
            self.skipSysUninstall(_("you were not confirming"))
        else:
            cmd = "rm -fr /usr/lib/enigma2/python/Plugins/SystemPlugins/%s"  % (self.systouninstall)
            os.system(cmd)
            self.session.open(MessageBox, _("Systemplugin has been removed!"), type = MessageBox.TYPE_INFO,timeout = 5)


    def skipSysUninstall(self,reason):
        self.session.open(MessageBox,_("Remove of systemplugin was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


    def getSysUnlist(self):
        systouninstall = []
        for folder in os.listdir("/usr/lib/enigma2/python/Plugins/SystemPlugins/"):
            if not folder.startswith("__init"):
                systouninstall.append(( folder, "%s" % folder ))
        return systouninstall

class SkinRemove(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.askForSkin,ChoiceBox,_("Select skin to remove!"),self.getSkinUnlist())

    def askForSkin(self,skintouninstall):
        if skintouninstall is None:
            self.skipSkinUninstall(_("No skin selected"))
        else:
            self.skintouninstall=skintouninstall[1]
            self.session.openWithCallback(self.UserScriptUninstall,MessageBox,_("remove %s?") % self.skintouninstall,MessageBox.TYPE_YESNO)
            
    def UserScriptUninstall(self,answer):
        if answer is None:
            self.skipSkinUninstall(_("answer is None"))
        if answer is False:
            self.skipSkinUninstall(_("you were not confirming"))
        else:
            cmd = "rm -fr /usr/share/enigma2/%s"  % (self.skintouninstall)
            os.system(cmd)
            self.session.open(MessageBox, _("Skin has been removed!"), type = MessageBox.TYPE_INFO,timeout = 5)


    def skipSkinUninstall(self,reason):
        self.session.open(MessageBox,_("Remove of skin was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


    def getSkinUnlist(self):
        skintouninstall = []
        for folder in os.listdir("/usr/share/enigma2/"):
            exception1 = ('__init', 'default', 'skin_defau', 'countrie', 'deale', 'extension', 'po', 'rc_models', 'spinner', 'display')
            exception2 = ('xml', 'conf', 'png', 'mvi', 'jpg', 't1', 't2', 'conf')
            if not folder.startswith(exception1) and not folder.endswith(exception2):
                skintouninstall.append(( folder, "%s" % folder ))
        return skintouninstall


class CrashlogRemove(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.UserScriptUninstall,MessageBox,_("Remove crashlogs?"),MessageBox.TYPE_YESNO)

    def UserScriptUninstall(self,answer):
        if answer is None:
            self.skipCrashUninstall(_("answer is None"))
        if answer is False:
            self.skipCrashUninstall(_("you were not confirming"))
        else: 
            #Nasty! But have no time right now to check the path where user store the logs..... latter
            cmd = "rm -f /hdd/enigma2_crash_*.log"
            cmd1 = "rm -f /hdd/Enigma2-debug-*.log"
            os.system(cmd)
            os.system(cmd1)
            cmd = "rm -f /home/root/logs/enigma2_crash_*.log"
            cmd1 = "rm -f /home/root/logs//Enigma2-debug-*.log"
            os.system(cmd)
            os.system(cmd1)
            self.session.open(MessageBox, _("Crashlogs have been removed!"), type = MessageBox.TYPE_INFO,timeout = 5)


    def skipCrashUninstall(self,reason):
        self.session.open(MessageBox,_("Remove of crashlogs was canceled, because %s") % reason, MessageBox.TYPE_ERROR)



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
        res.append(MultiContentEntryText(pos=(60, 5), size=(900, 38), font=0, text=name))
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
                if element[0] == "      ":
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