#'''
#@author: terrajoe
#
#Created on 13.03.2011
#changed on 20.09.2015
#'''
##########################################################
# -*- coding: utf-8 -*-

from __init__ import _
from Screens.Screen import Screen
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.Console import Console
from Components.FileList import FileList
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigYesNo, NoSave, config, ConfigFile, ConfigNothing, ConfigSelection
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.Directories import fileExists
from enigma import eConsoleAppContainer, eTimer
from Tools.BoundFunction import boundFunction
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label

import os



##################################################################################################################################################################################

configfile = ConfigFile()

def checkDev():
	try:
		mydev = []
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			if (line.find('/cf') != -1):
				mydev.append(('/media/cf/','COMPACT FLASH'))
			if (line.find('/media/usb') != -1):
				mydev.append(('/media/usb/','USB'))
			if (line.find('/hdd') != -1):
				mydev.append(('/media/hdd/','HDD'))
			if (line.find('/media/usb1') != -1):
				mydev.append(('/media/usb1/','USB1'))
			if (line.find('/media/usb2') != -1):
				mydev.append(('/media/usb2/','USB2'))
			if (line.find('/media/usb3') != -1):
				mydev.append(('/media/usb3/','USB3'))
			if (line.find('/media/mmc1') != -1):
				mydev.append(('/media/mmc1/','MMC'))	
		f.close()
		if mydev:
			return mydev
	except:
		return None

##################################################################################################################################################################################

class Swap(Screen, ConfigListScreen):
	__module__ = __name__
	
	skin = """
		<screen position="center,center" size="620,440">
			<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />
			<widget name="conn" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center"  foregroundColor="#ffffff" backgroundColor="#6565ff" />
			<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb.png" position="420,200" size="180,180" alphatest="on" />
			<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />
			<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["oktext"] = Label(_("Save"))
		self["canceltext"] = Label(_("Exit"))
		self['conn'] = Label("")
		self['conn'].hide()
		self.active = False
		self.loc = ''
		self.size = 0
		self.activityTimer = eTimer()
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], 
		{
			"red": self.close,
			"back": self.close,
			"green": self.saveSwap
		})
		self.loadSetting()
		self.onShown.append(self.setWindowTitle)
		
	def setWindowTitle(self):
		self.setTitle(_("Manage Swap File"))
	
	def loadSetting(self):
		self.mydev = checkDev()
		mystat = self.findSwap()
		del self.list[:]
		if self.mydev is None:
			self.close
		else:
			self.loc = self.mydev[0][0]
			self.size = 32768
			if mystat != None:
				self.active = True
				self.loc = mystat[0]
				self.size = mystat[1] + 8
		
			self.swap_active = NoSave(ConfigYesNo(default = self.active))
			self.list.append(getConfigListEntry(_('Activate Swap File?'), self.swap_active))
			self.swap_size = NoSave(ConfigSelection(default = self.size, choices =[
												(8192,'8 MB'), (16384,'16 MB'), (32768,'32 MB'),
												(65536,'64 MB'), (131072,'128 MB'), (262144,'256 MB'),
												(524288,'512 MB'), (1048576,'1024 MB'), (2097152,'2048 MB')]))
			self.list.append(getConfigListEntry(_('Swap file size'), self.swap_size))
			self.swap_location = NoSave(ConfigSelection(default = self.loc, choices = self.mydev))
			self.list.append(getConfigListEntry(_('Swap file location'), self.swap_location))
			self['config'].list = self.list
			self['config'].l.setList(self.list)
	
	def saveSwap(self):
		self['conn'].show()
		self['conn'].setText(_('Saving swap config. Please wait...'))
		self.activityTimer.timeout.get().append(self.Dsave)
		self.activityTimer.start(500, False)
		
	def Dsave(self):
		self.activityTimer.stop()
		swapfile = self.swap_location.value.strip() + 'swapfile'
		cmd = ''
		if (self.swap_active.value) and (not self.active):
			f = open("/etc/enigma2/.swap", "w")
			f.write("%s" % swapfile)
			f.close()
			cmd += "echo 'Creating swap file...'"
			cmd += ' && '
			cmd += 'dd if=/dev/zero of=' + swapfile + ' bs=1024 count=' + str(self.swap_size.value)
			cmd += ' && '
			cmd += "echo 'Creating swap device...'"
			cmd += ' && '
			cmd += 'mkswap ' + swapfile
			cmd += ' && '
			cmd += "echo 'Activating swap device...'"
			cmd += ' && '
			cmd += 'swapon ' + swapfile
			self.session.openWithCallback(self.scriptReturn, PBConsole, cmd, _('Creating Swap file...'))
		elif (not self.swap_active.value) and (self.active):
			os.system("rm -fr /etc/enigma2/.swap")
			cmd += "echo 'Deactivating swap device...'"
			cmd += ' && '
			cmd += 'swapoff ' + swapfile
			cmd += ' && '
			cmd += "echo 'Removing swap file...'"
			cmd += ' && '
			cmd += 'rm -f ' + swapfile
			self.session.openWithCallback(self.scriptReturn, PBConsole, cmd, _('Deleting Swap file...'))
		else:
			self['conn'].setText(_('Nothing to do!'))

	def scriptReturn(self, *answer):
		if answer[0] == PBConsole.EVENT_DONE:
			self['conn'].setText(_('Swap process completed successfully!'))
		else:
			self['conn'].setText(_('Swap process killed by user!'))
		self.loadSetting()

	def findSwap(self):
		try:
			myswap = []
			f = open('/proc/swaps', 'r')
			for line in f.readlines():
				if (line.find('/swapfile') != -1):
					myswap = line.strip().split()
			f.close()
			if myswap:
				return '/media/' + myswap[0].split("/")[2] + "/", int(myswap[2])
		except:
			return None 

##################################################################################################################################

class PBConsole(Screen):
	skin = """
		<screen position="center,center" size="600,350" >
			<widget name="text" position="20,20" size="560,270" font="Regular;18"/>
			<eLabel position="0,309" size="600,2" backgroundColor="grey" zPosition="5"/>
			<widget name="canceltext" position="0,310" zPosition="1" size="600,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />
			<widget name="oktext" position="0,310" zPosition="1" size="600,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
		</screen>"""
		
	EVENT_DONE = 10
	EVENT_KILLED = 5
	EVENT_CURR = 0
	
	def __init__(self, session, cmd, Wtitle, large = False):
		Screen.__init__(self, session)
		self.cmd = cmd
		self.Wtitle = Wtitle
		self.callbackList = []
		if large:
			self.skinName = ["PBConsole", "PBConsoleL" ]
		self["text"] = ScrollLabel("")
		self["oktext"] = Label(_("OK"))
		self["canceltext"] = Label(_("Cancel"))
		self["actions"] = ActionMap(["WizardActions", "DirectionActions",'ColorActions'], 
		{
			"ok": self.cancel,
			"back": self.cancel,
			"up": self["text"].pageUp,
			"down": self["text"].pageDown,
			"red": self.stop,
			"green": self.cancel
		}, -1)
		self["oktext"].hide()
		self.autoCloseTimer = eTimer()
		self.autoCloseTimer.timeout.get().append(self.cancel)
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(self.Wtitle)
	
	def startRun(self):
		print "Console: executing in run the command:", self.cmd
		if self.container.execute(self.cmd):
			self.runFinished(-1)

	def runFinished(self, retval):
		self.EVENT_CURR = self.EVENT_DONE
		self["text"].setText(self["text"].getText() + _('Done') + '\n')
		self["text"].setText(self["text"].getText() + _('Please Press OK Button to close windows!') + '\n')
		self["oktext"].show()
		self["canceltext"].hide()
		if autocloseconsole.value:
			if int(autocloseconsoledelay.value) != 0:
				self.autoCloseTimer.startLongTimer(int(autocloseconsoledelay.value))
			else:
				self.cancel()
	
	def stop(self):
		if self.isRunning():
			self.EVENT_CURR = self.EVENT_KILLED
			self["text"].setText(self["text"].getText() + _('Action killed by user') + '\n')
			self.container.kill()
			self["oktext"].show()
			self["canceltext"].hide()
			if autocloseconsole.value:
				if int(autocloseconsoledelay.value) != 0:
					self.autoCloseTimer.startLongTimer(int(autocloseconsoledelay.value))
				else:
					self.cancel()
	
	def cancel(self):
		if not self.isRunning():
			if self.autoCloseTimer.isActive():
				self.autoCloseTimer.stop()
			del self.autoCloseTimer
			self.container.appClosed.remove(self.runFinished)
			self.container.dataAvail.remove(self.dataAvail)
			del self.container.dataAvail[:]
			del self.container.appClosed[:]
			del self.container
			self.close(self.EVENT_CURR)

	def dataAvail(self, str):
		self["text"].setText(self["text"].getText() + str)

	def isRunning(self):
		return self.container.running()
		
autocloseconsole = ConfigYesNo(default = True)
autocloseconsoledelay = ConfigSelection(default = "10", choices = [
		("0", _("No Delay")),("1", "1 " + _("second")),("2", "2 " + _("seconds")), 
		("3", "3 " + _("seconds")),("4", "4 " + _("seconds")),("5", "5 " + _("seconds")),
		("6", "6 " + _("seconds")),("7", "7 " + _("seconds")),("10", "10 " + _("seconds"))])          
