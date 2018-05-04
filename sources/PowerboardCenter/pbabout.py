from enigma import *
from Screens.Screen import Screen
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Components.ActionMap import ActionMap

class PBAboutTeam(Screen):

	def __init__(self, session, args = 0):
		self.skin = """
	<screen name="AboutTeam" position="center,center" size="500,500" title="Powerboard Team">
		<eLabel text="Many thanks to all developers and betatesters:" position="10,10" size="500,20" font="Regular; 18" halign="left" />
		<eLabel text="Developer:" position="10,40" size="200,20" font="Regular; 18" halign="left" />
		<eLabel text="marcus.past" position="10,63" size="200,24" font="Regular; 20" halign="center" />
		<eLabel text="Terrajoe" position="212,63" size="200,24" font="Regular; 20" halign="center" />
		<eLabel text="Stibbich" position="10,89" size="200,24" font="Regular; 20" halign="center" />
		<eLabel text="graugans" position="212,89" size="200,24" font="Regular; 20" halign="center" />
		<eLabel text="Betatester ans Skinner:" position="10,120" size="200,20" font="Regular; 18" halign="left" />
		<eLabel text="deathwalker" position="10,143" size="200,24" font="Regular;20" halign="center" />
		<eLabel text="gorski" position="212,143" size="200,24" font="Regular;20" halign="center" />
		<eLabel text="Robodoc" position="10,168" size="200,24" font="Regular;20" halign="center" />
		<eLabel text="Trial" position="212,168" size="200,24" font="Regular;20" halign="center" />
		<eLabel text="FrancHR" position="10,194" size="250,24" font="Regular;20" halign="center" />
		<eLabel text="Support:" position="10,246" size="200,20" font="Regular; 18" halign="left" />
		<eLabel text="www.pb-powerboard.com" position="10,272" size="250,24" font="Regular;20" halign="center" />
		<eLabel text="in memorian to bosmann" position="10,376" size="250,24" font="Regular;20" halign="center" />
		<ePixmap position="285,285" size="250,250" zPosition="-10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb.png" transparent="0" alphatest="on" />
	</screen>"""

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.close,
			"cancel": self.close,
		}, -1)

	def quit(self):
		self.close()
