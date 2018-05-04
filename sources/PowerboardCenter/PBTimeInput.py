from Screens.Screen import Screen
from Components.config import ConfigClock, ConfigDateTime, getConfigListEntry
from Components.ActionMap import NumberActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
import time
import datetime

class PBTimeInput(Screen, ConfigListScreen):
    skin = """
        <screen name="PBTimeInput" position="center,center" size="400,200" title="Time input">
            <widget name="cancel" pixmap="skin_default/buttons/red.png" position="10,0" size="140,40" alphatest="on" />
            <widget name="ok" pixmap="skin_default/buttons/green.png" position="250,0" size="140,40" alphatest="on" />
            <widget name="canceltext" position="10,0" zPosition="1" size="140,40" font="Regular;19" halign="center" valign="center" transparent="1" />
            <widget name="oktext" position="250,0" zPosition="1" size="140,40" font="Regular;19" halign="center" valign="center" transparent="1" />
            <widget name="config" position="10,40" size="380,150" />
        </screen>"""

    def __init__(self, session, config_time=None, config_date=None):
        Screen.__init__(self, session)
        self["oktext"] = Label(_("OK"))
        self["canceltext"] = Label(_("Cancel"))
        self["ok"] = Pixmap()
        self["cancel"] = Pixmap()

        self.createConfig(config_date, config_time)

        self["actions"] = NumberActionMap(["SetupActions"],
        {
            "ok": self.keySelect,
            "save": self.keyGo,
            "cancel": self.keyCancel,
        }, -2)

        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self.createSetup(self["config"])

    def createConfig(self, conf_date, conf_time):
        self.save_mask = 0
        if conf_time:
            self.save_mask |= 1
        else:
            conf_time = ConfigClock(default = time.time()),
        if conf_date:
            self.save_mask |= 2
        else:
            conf_date = ConfigDateTime(default = time.time(), formatstring = _("%d.%B %Y"), increment = 86400)
        self.timeinput_date = conf_date
        self.timeinput_time = conf_time

    def createSetup(self, configlist):
        self.list = [
            getConfigListEntry(_("Time"), self.timeinput_time)
        ]
        configlist.list = self.list
        configlist.l.setList(self.list)

    def keySelect(self):
        self.keyGo()

    def getTimestamp(self, date, mytime):
        d = time.localtime(date)
        dt = datetime.datetime(d.tm_year, d.tm_mon, d.tm_mday, mytime[0], mytime[1])
        return int(time.mktime(dt.timetuple()))

    def keyGo(self):
        time = self.getTimestamp(self.timeinput_date.value, self.timeinput_time.value)
        if self.save_mask & 1:
            self.timeinput_time.save()
        if self.save_mask & 2:
            self.timeinput_date.save()
        self.close((True, time))

    def keyCancel(self):
        if self.save_mask & 1:
            self.timeinput_time.cancel()
        if self.save_mask & 2:
            self.timeinput_date.cancel()
        self.close((False,))
