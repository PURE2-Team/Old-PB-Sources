#
#  BackupPathSet E2
#
#  Coded by pb-team (c) 2011
#  Support: www.pb-powerboard.com
#

from __init__ import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigSelection, getConfigListEntry, NoSave, ConfigText, ConfigDirectory
from Components.ConfigList import ConfigListScreen
from Components.FileList import FileList
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
import os

config.misc.backup_path = ConfigText(default="/media")

#Crash verhindern, wenn nix in der config steht
if os.path.exists("%s" % (config.misc.backup_path.value)) is False:
	config.misc.backup_path.value = "/media"

class SetBackupPath(Screen, ConfigListScreen):

	skin = """
		<screen position="center,center" size="560,320" title="BackupPathSet" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
			<widget render="Label" source="key_red" position="0,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget render="Label" source="key_green" position="140,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget name="config" position="20,50" size="520,250" scrollbarMode="showOnDemand" />
		</screen>""" 

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		path = config.misc.backup_path.value
		self.backup_path = NoSave(ConfigDirectory(default = path))
		list = []
		list.append(getConfigListEntry(_("Backup path"), self.backup_path))	
		ConfigListScreen.__init__(self, list)
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keySelect,
			"green": self.save,
			"red": self.exit,
			"cancel": self.exit,
		}, -1)

	def save(self):
		config.misc.backup_path.value = self.backup_path.value
		config.misc.backup_path.save()
		config.misc.backup_path.changed()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply the new backuppath\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))
		
	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)

	def exit(self):
		self.close()
	
	def keySelect(self):
		self.session.openWithCallback(self.pathSelected,backupPath,self.backup_path.value)

	def pathSelected(self, res):
		if res is not None:
			self.backup_path.value = res

class backupPath(Screen):
	skin = """<screen position="center,center" size="560,320" title="Select path for Backups">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
			<widget name="target" position="0,60" size="540,22" valign="center" font="Regular;22" />
			<widget name="filelist" position="0,100" zPosition="1" size="560,220" scrollbarMode="showOnDemand"/>
			<widget render="Label" source="key_red" position="0,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget render="Label" source="key_green" position="140,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
		</screen>"""
	def __init__(self, session, initDir):
		Screen.__init__(self, session)
		inhibitDirs = ["/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
		inhibitMounts = []
		self["filelist"] = FileList(initDir, showDirectories = True, showFiles = False, inhibitMounts = inhibitMounts, inhibitDirs = inhibitDirs)
		self["target"] = Label()
		self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "PiconSelectActions"],
		{
			"back": self.cancel,
			"left": self.left,
			"right": self.right,
			"up": self.up,
			"down": self.down,
			"ok": self.ok,
			"green": self.green,
			"red": self.cancel
			
		}, -1)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))

	def cancel(self):
		self.close(None)

	def green(self):
		self.close(self["filelist"].getSelection()[0])

	def up(self):
		self["filelist"].up()
		self.updateTarget()

	def down(self):
		self["filelist"].down()
		self.updateTarget()

	def left(self):
		self["filelist"].pageUp()
		self.updateTarget()

	def right(self):
		self["filelist"].pageDown()
		self.updateTarget()

	def ok(self):
		if self["filelist"].canDescent():
			self["filelist"].descent()
			self.updateTarget()

	def updateTarget(self):
		currFolder = self["filelist"].getSelection()[0]
		if currFolder is not None:
			self["target"].setText(currFolder)
		else:
			self["target"].setText(_("Invalid Location"))		
