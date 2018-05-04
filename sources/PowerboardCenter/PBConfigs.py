# PBConfigs
# Coded by Stibbich
# 2012-03-26

#2014-10-10
# add Ocram feeds ON/OFF

from __init__ import _
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.SystemInfo import SystemInfo
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigBoolean, ConfigYesNo
from Components.ActionMap import ActionMap
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
import os
import re
import string
from enigma import eConsoleAppContainer

class PowerboardSetup(Screen, ConfigListScreen):

	skin = """
		<screen position="center,center" size="460,400" title="PB-Settings" >
			<widget name="config" position="10,10" size="441,328" scrollbarMode="showOnDemand" />
			<widget name="key_red" position="98,350" zPosition="2" size="90,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<ePixmap name="red" position="98,350" zPosition="1" size="90,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/key-red.png" transparent="1" alphatest="on" />
			<widget name="key_blue" position="241,350" zPosition="2" size="90,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<ePixmap name="blue" position="241,350" zPosition="1" size="90,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/key-blue.png" transparent="1" alphatest="on" />
		</screen>"""


	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.decodeinfo = 0
		self.emumessage = 0
		self.netinfo = 0
		self.caminfo = 0
		self.uselabelmount = 0
		self.ocram = os.path.isfile('/etc/opkg/ocram.conf')

		self.load()
		
		self.list = []
		self.list.append(getConfigListEntry(_("Hide Decode-Info"), ConfigYesNo(default=self.decodeinfo)))
		self.list.append(getConfigListEntry(_("Hide only Decode-Emu"), ConfigYesNo(default=self.emumessage)))
		self.list.append(getConfigListEntry(_("Hide only Decode-Net"), ConfigYesNo(default=self.netinfo)))
		self.list.append(getConfigListEntry(_("Hide Cam-Info"), ConfigYesNo(default=self.caminfo)))
		self.list.append(getConfigListEntry(_("Use label mount"), ConfigYesNo(default=self.uselabelmount)))
		self.list.append(getConfigListEntry(_("Ocram feeds for picons active"), ConfigYesNo(default=self.ocram)))

		ConfigListScreen.__init__(self, self.list, session = session)
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"red": self.ok,
					#"green": self.green,
					"blue": self.keyCancel,
					"cancel": self.keyCancel,
				}, -2)
				
		self["key_green"] = Button("")
		self["key_red"] = Button(_("Ok"))
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")

	def load(self):
		try:
			f = open("/etc/enigma2/pbsettings", "r")
		except Exception, e:
			return
			
		import re
		commentRe = re.compile(r"#(.*)")
		entryRe = re.compile(r"(.*)=(.*)")
		
		for line in f.readlines(): 
			comment = re.findall(commentRe, line)
			if not comment:
				entry = re.findall(entryRe, line)
				if entry:
					key = entry[0][0].strip()
					value = entry[0][1].strip()
					if key == "decodeinfo":
						self.decodeinfo = int(value)
					elif key == "emumessage":
						self.emumessage = int(value)
					elif key == "netinfo":
						self.netinfo = int(value)
					elif key == "caminfo":
						self.caminfo = int(value)
					elif key == "uselabelmount":
						self.uselabelmount = int(value)
						
		f.close()

	def save(self):
		try:
			f = open("/etc/enigma2/pbsettings", "w")
		except Exception, e:
			return
		
		f.write("decodeinfo=%d\n" % (self.decodeinfo))
		f.write("emumessage=%d\n" % (self.emumessage))
		f.write("netinfo=%d\n" % (self.netinfo))
		f.write("caminfo=%d\n" % (self.caminfo))
		f.write("uselabelmount=%d\n" % (self.uselabelmount))
		
		if self.uselabelmount == 1:
			os.system("touch /etc/enigma2/.labelmount")
		else:
			os.system("rm /etc/enigma2/.labelmount")
		
		if not (self.list[5][1].value == self.ocram):
			if self.list[5][1].value: # make ocram.conf
				os.system('echo "src/gz ocram-picons http://picons.org/downloads/ipk" > /etc/opkg/ocram.conf')
			else:
				os.system("rm -f /etc/opkg/ocram.conf")

		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply the new settings\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)

	def ok(self):
		self.decodeinfo = self.list[0][1].getValue()
		self.emumessage = self.list[1][1].getValue()
		self.netinfo = self.list[2][1].getValue()
		self.caminfo = self.list[3][1].getValue()
		self.uselabelmount = self.list[4][1].getValue()
		
		self.save()
