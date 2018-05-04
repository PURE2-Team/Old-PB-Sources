# 2011-10-11
##Edited by Franc 25.05.2016

Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from Screens.Screen import Screen
from enigma import eConsoleAppContainer
from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_ACTIVE_SKIN
from Tools.LoadPixmap import LoadPixmap

from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest

import string



def AddOnCategoryComponent(name, png):
	res = [ name ]
	# Estuary - Start Here 
	if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
		res.append(MultiContentEntryText(pos=(140, 5), size=(800, 71), font=0, text=name))
		res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(100, 71), png = png))
	else:
		# Estuary - Cut Here (next two lines one Tab back)
		res.append(MultiContentEntryText(pos=(140, 5), size=(300, 25), font=0, text=name))
		res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(100, 50), png = png))
	
	return res


def AddOnDownloadComponent(plugin, name):
	res = [ plugin ]
	text = ""
	if plugin.installed_version and plugin.installed_version != plugin.version:
		text = "%s -> updatable to %s" % (plugin.installed_version, plugin.version)
	elif plugin.installed_version:
		text = "Installed package version: %s" % (plugin.installed_version)
	else:
		text = "Package version: %s" % (plugin.version)
	
	# Estuary - Start Here 
	if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
		res.append(MultiContentEntryText(pos=(140, 5), size=(800, 38), font=0, text = name))
		res.append(MultiContentEntryText(pos=(140, 30), size=(800, 17), font=1, text=plugin.description))
		res.append(MultiContentEntryText(pos=(140, 46), size=(800, 17), font=1, text=text))
	else:
		# Estuary - Cut Here (next three lines one Tab back)
		res.append(MultiContentEntryText(pos=(140, 5), size=(480, 25), font=0, text = name))
		res.append(MultiContentEntryText(pos=(140, 30), size=(480, 17), font=1, text=plugin.description))
		res.append(MultiContentEntryText(pos=(140, 46), size=(480, 17), font=1, text=text))

	if plugin.icon is None:
		png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/icons/plugin.png"))
	else:
		png = plugin.icon

	res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(100, 50), png = png))

	if plugin.statusicon is None:
		png1 = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/icons/plugin.png"))
	else:
		png1 = plugin.statusicon

	res.append(MultiContentEntryPixmapAlphaTest(pos=(120, 17), size=(12, 12), png = png1))
	
	return res

class AddOnDescriptor:
	def __init__(self, name = "", what = "", description = "", status = 0, version = "", icon = None, statusicon = None, installed_version = ""):
		self.name = name
		self.what = what
		self.description = description
		self.status = status
		self.version = version
		if icon is None:
			self.icon = None
		else:
			self.icon = icon
		
		if statusicon is None:
			self.statusicon = None
		else:
			self.statusicon = statusicon
		self.installed_version = installed_version

class AddOn:
	def __init__(self, name = "", version = "", description = "", status = 0, installed_version = ""):
		self.name = name
		self.version = version
		self.description = description
		self.status = status
		self.installed_version = installed_version

class PowerboardExpertInstaller(Screen):

	skin = """
		<screen name="PowerboardExpertInstaller" position="center,center" size="560,420" title="Powerboard Expert Installer">
			<widget name="text" position="0,0" zPosition="1" size="560,430" font="Regular;20" halign="center" valign="center" />
			<widget name="list" position="10,10" zPosition="2" size="540,405" scrollbarMode="showOnDemand" />
		</screen>"""
		

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)
		
		self.list = []
		self["list"] = PluginList(self.list)
		self.pluginlist = []
		self.expanded = []
		self.addoninstalled = []
		self.found = 0
		
		self["text"] = Label(_("Downloading all available ipk from feed. Please wait..."))
		
		self.run = 0

		self.remainingdata = ""

		self["actions"] = ActionMap(["WizardActions"], 
		{
			"ok": self.go,
			"back": self.close,
		})

	def go(self):
		sel = self["list"].l.getCurrentSelection()

		if sel is None:
			return

		if type(sel[0]) is str: # category
			if sel[0] in self.expanded:
				self.expanded.remove(sel[0])
			else:
				self.expanded.append(sel[0])
			self.updateList()
		else:
			if sel[0].status == 0 and not "picon" in sel[0].name:
				self.session.openWithCallback(self.runForceInstallCallBack, DialogForceInstall, _("Do you really want to download the addon %s?") % sel[0].name)
			elif sel[0].status == 0 and "picon" in sel[0].name:
				self.session.openWithCallback(self.runPiconInstallCallBack, DialogPiconInstall, _("Where do you want to install the picons?"))
			elif sel[0].status == 1:
				self.session.openWithCallback(self.runForceRemoveCallBack, DialogForceRemove, _("Do you really want to remove the ipk %s or reinstall it?") % sel[0].name)
			elif sel[0].status == 2:
				self.session.openWithCallback(self.runDeleteUpdateCallBack, DialogUpdateDelete, _("The ipk %s is already installed and an update is available. What do you want to do?") % sel[0].name)

	def runForceRemoveCallBack(self, answer):
		print "answer:", answer
		if answer == 0:
			self.session.openWithCallback(self.installFinished, Console, cmdlist = ["opkg remove " + self["list"].l.getCurrentSelection()[0].name])
		elif answer == 1:
			self.session.openWithCallback(self.installFinished, Console, cmdlist = ["opkg remove --nodeps " + self["list"].l.getCurrentSelection()[0].name])
		elif answer == 2:
			self.session.openWithCallback(self.installFinished, Console, cmdlist = ["opkg remove --nodeps " + self["list"].l.getCurrentSelection()[0].name + "; opkg install " + self["list"].l.getCurrentSelection()[0].name])

	def runDeleteUpdateCallBack(self, answer):
		print "answer:", answer
		if answer == 0:
			self.session.openWithCallback(self.installFinished, Console, cmdlist = ["opkg install " + self["list"].l.getCurrentSelection()[0].name])
		elif answer == 1:
			self.session.openWithCallback(self.installFinished, Console, cmdlist = ["opkg remove " + self["list"].l.getCurrentSelection()[0].name])
			
	def runForceInstallCallBack(self, answer):
		print "answer:", answer
		if answer == 0:
			self.session.openWithCallback(self.installFinished, Console, cmdlist = ["opkg install --force-overwrite " + self["list"].l.getCurrentSelection()[0].name])
		elif answer == 1:
			self.session.openWithCallback(self.installFinished, Console, cmdlist = ["opkg install " + self["list"].l.getCurrentSelection()[0].name])

	def runPiconInstallCallBack(self, answer):
		print "answer:", answer
		self.session.openWithCallback(self.installFinished, Console, cmdlist = ["opkg install -d %s --force-overwrite " %answer + self["list"].l.getCurrentSelection()[0].name])

	def setWindowTitle(self):
		self.setTitle(_("Powerboard Expert Installer"))

	def startRun(self):
		print "startRun(self):"
		self["list"].instance.hide()
		self.container.execute("opkg update")

	def installFinished(self):
		# was ist eigentlich passiert? Aktualisiere...
		self["list"].instance.hide()
		try:
			f = open("/usr/lib/opkg/info/"+self["list"].l.getCurrentSelection()[0].name+".control", "r")
			addoncontent = f.read()
			f.close()
		except:
			addoncontent = ""
		name = ""
		version = ""
		description = ""
		addoncontentInfo = addoncontent.split("\n")
		for line in addoncontentInfo:
			if line.startswith("Package: "):
				name = line[9:]
			if line.startswith("Version: "):
				version = line[9:]
			if line.startswith("Description: "):
				description = line[13:]
		if name != "" and version != "":
			for aa in self.pluginlist:
				if aa.name == name:
					if version == self["list"].l.getCurrentSelection()[0].version:
						aa.status = 1
						aa.installed_version = aa.version
					else:
						aa.status = 2
		else:
			for aa in self.pluginlist:
				if aa.name == self["list"].l.getCurrentSelection()[0].name:
					aa.status = 0
		self.updateList()
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self["list"].instance.show()

	def runFinished(self, retval):
		self.remainingdata = ""
		if self.run == 0:
			self.run = 1
			self.container.execute("opkg list-installed")
		elif self.run == 1:
			self.run = 2
			self.container.execute("opkg list")
		elif self.run == 2:
			if len(self.pluginlist) > 0:
				self.updateList()
				self["list"].instance.show()
			else:
				self["text"].setText(_("No new plugins found"))

	def dataAvail(self, str):
		#prepend any remaining data from the previous call
		str = self.remainingdata + str
		#split in lines
		lines = str.split('\n')
		#'str' should end with '\n', so when splitting, the last line should be empty. If this is not the case, we received an incomplete line
		if len(lines[-1]):
			#remember this data for next time
			self.remainingdata = lines[-1]
			lines = lines[0:-1]
		else:
			self.remainingdata = ""
		
		for x in lines:
			plugin = x.split(" - ")
			if len(plugin) >= 2 and self.run == 1:
				self.addoninstalled.append(AddOn(name = plugin[0], version = plugin[1], status = 1))
			elif len(plugin) == 3 and self.run == 2:
				flagStatus = 0 # nicht installiert
				installedVersion = ""
				for cb in self.addoninstalled:
					if plugin[0] == cb.name:
						if plugin[1] == cb.version:
							if cb.status != 2:
								flagStatus = 1 # installiert
								installedVersion = cb.version
							else:
								flagStatus = -1 # brauchen wir nicht, da schon als update gekennzeichnet
						else:
							cb.status = 2
							flagStatus = 2 # update
							installedVersion = cb.version
				if flagStatus != -1:
					self.pluginlist.append(AddOn(name = plugin[0], version = plugin[1], description = plugin[2], status = flagStatus, installed_version = installedVersion))

	def updateList(self):
		self.list = []
		# Estuary - Start Here 
		if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
			expandableIcon = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/expandable-plugins.png'))
			expandedIcon = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/expanded-plugins.png'))
			verticallineIcon = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/verticalline-plugins.png'))
		else:
		# Estuary - Cut Here (next three lines one Tab back)
			expandableIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/expandable-plugins.png'))
			expandedIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/expanded-plugins.png'))
			verticallineIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/verticalline-plugins.png'))
		installedIcon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/PowerboardCenter/pics/green_small.png"))
		notinstalledIcon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/PowerboardCenter/pics/red_small.png"))
		updateIcon = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/PowerboardCenter/pics/blue_small.png"))
		self.plugins = {}
		for x in self.pluginlist:
			temp = ""
			temp1 = x.name
			if x.name.startswith('a') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "a-"+x.name
			elif x.name.startswith('b') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "b-"+x.name
			elif x.name.startswith('c') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "c-"+x.name
			elif x.name.startswith('d') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "d-"+x.name
			elif x.name.startswith('e') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "e-"+x.name
			elif x.name.startswith('f') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "f-"+x.name
			elif x.name.startswith('g') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "g-"+x.name
			elif x.name.startswith('h') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "h-"+x.name
			elif x.name.startswith('i') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "i-"+x.name
			elif x.name.startswith('j') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "j-"+x.name
			elif x.name.startswith('k') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "k-"+x.name
			elif x.name.startswith('l') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "l-"+x.name
			elif x.name.startswith('m') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "m-"+x.name
			elif x.name.startswith('n') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "n-"+x.name
			elif x.name.startswith('o') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "o-"+x.name
			elif x.name.startswith('p') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "p-"+x.name
			elif x.name.startswith('q') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "q-"+x.name
			elif x.name.startswith('r') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "r-"+x.name
			elif x.name.startswith('s') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "s-"+x.name
			elif x.name.startswith('t') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "t-"+x.name
			elif x.name.startswith('u') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "u-"+x.name
			elif x.name.startswith('v') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "v-"+x.name
			elif x.name.startswith('w') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "w-"+x.name
			elif x.name.startswith('x') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "x-"+x.name
			elif x.name.startswith('y') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "y-"+x.name
			elif x.name.startswith('z') and not 'dbg' in x.name and not 'dev' in x.name:
				temp = "z-"+x.name
			else:
				continue
			split = temp.split('-', 1)
			if len(split) < 2:
				continue
			if not self.plugins.has_key(split[0]):
				self.plugins[split[0]] = []
			if x.status == 0:			
				pngstatus = notinstalledIcon
			elif x.status == 1:
				pngstatus = installedIcon
			elif x.status == 2:
				pngstatus = updateIcon
			else:
				pngstatus = None
			self.plugins[split[0]].append((AddOnDescriptor(name = x.name, what = split[0], description = x.description, icon = verticallineIcon, status = x.status, version = x.version, statusicon = pngstatus, installed_version = x.installed_version), split[1]))
		for x in self.plugins.keys():
			if x in self.expanded:
				self.list.append(AddOnCategoryComponent(x, expandedIcon))
				for plugin in self.plugins[x]:
					self.list.append(AddOnDownloadComponent(plugin[0], plugin[1]))
			else:
				self.list.append(AddOnCategoryComponent(x, expandableIcon))
		# Estuary - Start Here 
		if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
			self["list"].l.setItemHeight(71)
		else:
		# Estuary - Cut Here (next line one Tab back)
			self["list"].l.setItemHeight(65)
		self["list"].l.setList(self.list)

class DialogUpdateDelete(Screen):

	skin = """
		<screen name="DialogUpdateDelete" position="60,245" size="600,10" title="PowerboardExpertInstaller">
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
		self.list = [ (_("Update ipk"), 0), (_("Delete ipk"), 1) ]
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

class DialogForceInstall(Screen):

	skin = """
		<screen name="DialogForceInstall" position="60,245" size="600,10" title="PowerboardExpertInstaller">
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
		self.list = [ (_("Install ipk"), 0), (_("Force Install ipk"), 1) ]
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
		

class DialogForceRemove(Screen):

	skin = """
		<screen name="DialogForceRemove" position="60,245" size="600,10" title="PowerboardExpertInstaller">
		<widget name="text" position="65,8" size="520,0" font="Regular;22" />
		<widget name="QuestionPixmap" pixmap="skin_default/icons/input_question.png" position="5,5" size="53,53" alphatest="on" />
		<widget name="list" position="100,100" size="580,475" />
		<applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth = self.instance.size().width()
orgpos = self.instance.position()
textsize = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 50)
offset = 0
offset = 90
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
listsize = (wsizex, 110)
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
		self.list = [ (_("Remove ipk"), 0), (_("Remove ipk ignoring depends"), 1), (_("Reinstall ipk"), 2) ]
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
		print str



class DialogPiconInstall(Screen):

	skin = """
		<screen name="DialogPiconInstall" position="60,245" size="600,10" title="PowerboardAddOnManager">
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
offset = 90
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
listsize = (wsizex, 110)
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
		self.list.append("/usr/share/enigma2")
		if "/media/usb" in open("/proc/mounts").read():
			self.list.append("/media/usb")
		if "/media/usb1" in open("/proc/mounts").read():
			self.list.append("/media/usb1")
		if "/media/usb2" in open("/proc/mounts").read():
			self.list.append("/media/usb2")
		if "/media/usb3" in open("/proc/mounts").read():
			self.list.append("/media/usb3")
		if "/media/cf" in open("/proc/mounts").read():
			self.list.append("/media/cf")
		if "/media/hdd" in open("/proc/mounts").read():
			self.list.append("/media/hdd")
		if "/media/hdd1" in open("/proc/mounts").read():
			self.list.append("/media/hdd1")
		if "/media/hdd2" in open("/proc/mounts").read():
			self.list.append("/media/hdd2")
		if "/media/hdd3" in open("/proc/mounts").read():
			self.list.append("/media/hdd3")
		if "/media/mmc1" in open("/proc/mounts").read():
			self.list.append("/media/mmc1")
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
		self.close(self["list"].getCurrent())
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
		
