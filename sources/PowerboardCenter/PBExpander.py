# 2013-03-11
#
#@author: stibbich <stibbich@pb-powerboard.com>
# edited 31.08.2013
#
from __init__ import _
from Screens.Screen import Screen
from Components.ConfigList import *
from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.Label import Label
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Screens.Console import Console

from enigma import *
from Tools.Directories import fileExists
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.Input import Input
from Components.Label import Label
from Components.Button import Button
import os
import gettext
import re
import time
import subprocess


class Expander(Screen):
    skin = """
        <screen name="PB-Expander" position="center,center" size="650,420" title="PB-Expander" flags="wfNoBorder">
            <widget name="menu" position="45,84" size="425,300" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
            <eLabel text="Expand to mounted partition" position="20,8" size="485,50" font="Regular;28" backgroundColor="black" shadowOffset="-3,-3" shadowColor="black" transparent="1" />
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

        self.expanded = "0"
        if os.path.isfile("/etc/enigma2/.tanja"):
            self.expanded = "1"
        else:
            self.expanded = "0"

        list = []
        if self.expanded == "0":
            list.append(SimpleEntry(_("Expand to device"), "partitionmanager.png"))
        else:
            list.append(SimpleEntry(_("End outsourcing"), "partitionmanager.png"))
        list.append(SimpleEntry(_("Label Device"), "partitionmanager.png"))
        list.append(SimpleEntry(_("Swap-Manager"), "partitionmanager.png"))
        
        list.append(SimpleEntry(_("Devices Info"), "partitionmanager.png"))

        Screen.__init__(self, session)
        self['menu'] = ExtrasList(list)
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
            "ok": self.go,
            "cancel": self.cancel
        }, -1)


    def go(self):
        index = self['menu'].getSelectedIndex()
        if (index == 0) and self.expanded == "0":
            Expand(self.session)
        elif (index == 0) and self.expanded == "1":
            EndExpand(self.session)
        elif (index == 1):
            LabelDevice(self.session)
        elif (index == 2):
            from Plugins.Extensions.PowerboardCenter.swap import *
            self.session.open(Swap)
        elif (index == 3):
            self.session.open(DevicesInfo)

    def cancel(self):
        print "\n[menu] cancel\n"
        f = open("/etc/enigma2/pbsettings", "r")
        helper = f.readlines()
        f.close
        f = open("/etc/enigma2/pbsettings", "w")
        for line in helper:
            if "uselabelmount" not in line:
                f.write(line)
        f.write("uselabelmount=1")
        f.close()
        os.system("touch /etc/enigma2/.labelmount")
        os.system("cd /etc/init.d && ./mountpball")
        self.close(None)

class Expand(Screen):
    def __init__(self, session):
        self.session = session
        if os.path.isfile("/usr/bin/rsync"):
            self.session.openWithCallback(self.askForExpand,ChoiceBox,_("Select device to expand to!"),self.gettExpandTo())
        else:
            self.session.open(MessageBox, _("rsync is missing - installing it now"), type = MessageBox.TYPE_INFO, timeout = 30)
            os.system("opkg update && opkg install rsync")

    def askForExpand(self,getexpandto):
        if getexpandto is None:
            self.skipExpand(_("No device selected"))
        else:
            self.getexpandto=getexpandto[1]
            self.session.openWithCallback(self.UserScriptUninstall,MessageBox,_("Expand to %s?") % self.getexpandto,MessageBox.TYPE_YESNO)
            
    def UserScriptUninstall(self,answer):
        if answer is None:
            self.skipExpand(_("answer is None"))
        if answer is False:
            self.skipExpand(_("you were not confirming"))
        else:
            mnt = self.getexpandto
            print mnt
            fshelp = os.popen("mount | grep %s" %mnt)
            fs = fshelp.read().strip()
            fshelp.close()
            if "ext" in fs:
                if os.access("%s/tanja" %mnt, os.F_OK):
                    print "Loesche altes Verzeichnis, da moeglicherweise alte Sachen enthalten ist"
                    os.renames("%s/tanja" %mnt, "%s/delete" %mnt)
                    os.system("rm -rf %s/delete" %mnt)
                    print "Altes Verzeichnis geloescht"
                    os.system("mkdir %s/tanja" %mnt)
                    os.system("mkdir %s/tanja/usr" %mnt)
                    os.system("mkdir %s/tanja/usr/lib" %mnt)
                    os.system("mkdir %s/tanja/usr/lib/enigma2" %mnt)
                    os.system("mkdir %s/tanja/usr/lib/opkg" %mnt)
                    os.system("mkdir %s/tanja/usr/share" %mnt)
                    os.system("mkdir %s/tanja/usr/share/enigma2" %mnt)
                    os.system("mkdir %s/tanja/usr/local" %mnt)
                    if os.path.isdir("media/local"):
                        src4 = "/usr/local"
                        dst4 = "%s/tanja/usr/local" %mnt
                        n = subprocess.Popen("cp -rf %s %s" %(src4, dst4), shell=True)
                        n.wait
                        print n
                    else:
                        os.system("mkdir /usr/local")
                    print "Verzeichnisse erstellt"
                    src1 = "/usr/lib/enigma2/python"
                    src2 = "/usr/lib/opkg"
                    src3 = "/usr/share/enigma2"
                    dst1 = "%s/tanja/usr/lib/enigma2" %mnt
                    dst2 = "%s/tanja/usr/lib" %mnt
                    dst3 = "%s/tanja/usr/share" %mnt
                    o = subprocess.Popen("rsync -av %s %s" %(src1, dst1), shell=True)
                    o.wait
                    print o
                    p = subprocess.Popen("rsync -av %s %s" %(src2, dst2), shell=True)
                    p.wait
                    print p
                    q = subprocess.Popen("rsync -av %s %s" %(src3, dst3), shell=True)
                    q.wait
                    print q
                    print "Dateien kopiert"
                    r = subprocess.Popen("echo %s >> /etc/enigma2/.tanja" %mnt, shell=True)
                    r.wait
                    print "Kontroll-/Pfaddatei angelegt"
                    time.sleep(60)
                    self.session.open(MessageBox, _("Expanding ready!"), type = MessageBox.TYPE_INFO,timeout = 5)
                    os.system("reboot -nf")
                else:
                    os.system("mkdir %s/tanja" %mnt)
                    os.system("mkdir %s/tanja/usr" %mnt)
                    os.system("mkdir %s/tanja/usr/lib" %mnt)
                    os.system("mkdir %s/tanja/usr/lib/enigma2" %mnt)
                    os.system("mkdir %s/tanja/usr/lib/opkg" %mnt)
                    os.system("mkdir %s/tanja/usr/share" %mnt)
                    os.system("mkdir %s/tanja/usr/share/enigma2" %mnt)
                    os.system("mkdir %s/tanja/usr/local" %mnt)
                    if os.path.isdir("media/local"):
                        src4 = "/usr/local"
                        dst4 = "%s/tanja/usr/local" %mnt
                        n = subprocess.Popen("cp -rf %s %s" %(src4, dst4), shell=True)
                        n.wait
                        print n
                    else:
                        os.system("mkdir /usr/local")
                    print "Verzeichnisse erstellt"
                    src1 = "/usr/lib/enigma2/python"
                    src2 = "/usr/lib/opkg"
                    src3 = "/usr/share/enigma2"
                    dst1 = "%s/tanja/usr/lib/enigma2" %mnt
                    dst2 = "%s/tanja/usr/lib" %mnt
                    dst3 = "%s/tanja/usr/share" %mnt
                    o = subprocess.Popen("rsync -av %s %s" %(src1, dst1), shell=True)
                    o.wait
                    print o
                    p = subprocess.Popen("rsync -av %s %s" %(src2, dst2), shell=True)
                    p.wait
                    print p
                    q = subprocess.Popen("rsync -av %s %s" %(src3, dst3), shell=True)
                    q.wait
                    print q
                    print "Dateien kopiert"
                    r = subprocess.Popen("echo %s >> /etc/enigma2/.tanja" %mnt, shell=True)
                    r.wait
                    print "Kontroll-/Pfaddatei angelegt"
                    time.sleep(60)
                    self.session.open(MessageBox, _("Expanding ready!"), type = MessageBox.TYPE_INFO,timeout = 5)
                    os.system("reboot -nf")
            else:
                self.session.open(MessageBox, _("No ext-filesystem - please format (ext3 is recommended)"), type = MessageBox.TYPE_WARNING, timeout = 10)


    def skipExpand(self,reason):
        self.session.open(MessageBox,_("Expanding was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


    def gettExpandTo(self):
        getexpandto = []
        mounts = open("/proc/mounts", "r")
        for line in mounts:
            if "media/" in line:
                iliste = line.split(" ")
                inliste = iliste[1]
                getexpandto.append(( inliste, "%s" % inliste))
        return getexpandto
        mounts.close()


class EndExpand(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.UserScriptUninstall,MessageBox,_("Get rid of Expand?"),MessageBox.TYPE_YESNO)

    def UserScriptUninstall(self,answer):
        if answer is None:
            self.skipEndExpand(_("answer is None"))
        if answer is False:
            self.skipEndExpand(_("you were not confirming"))
        else:
            os.system("mv /etc/enigma2/.tanja /etc/enigma2/.tanjaremove")
            print "Kontrolldatei umbenannt um beim Neustarten das Verzeichnis zu loeschen"
            time.sleep(5)
            os.system("reboot -nf")

    def skipExpand(self,reason):
        self.session.open(MessageBox,_("Unexpanding was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


class LabelDevice(Screen):
    def __init__(self, session):
        self.session = session
        if os.path.isfile("/sbin/e2label"):
            self.session.openWithCallback(self.askForLabel,ChoiceBox,_("Select device to label!"),self.gettLabel())
        else:
            self.session.open(MessageBox, _("e2label is missing - installing it now"), type = MessageBox.TYPE_INFO, timeout = 30)
            os.system("opkg update && opkg install e2fsprogs-tune2fs")

    def askForLabel(self,getlabel):
        if getlabel is None:
            self.skipLabel(_("No device selected"))
        else:
            self.getlabel=getlabel[1]
            self.session.openWithCallback(self.UserScriptUninstall,MessageBox,_("Label %s?") % self.getlabel,MessageBox.TYPE_YESNO)

    def UserScriptUninstall(self,answer):
        if answer is None:
            self.skipLabel(_("answer is None"))
        if answer is False:
            self.skipLabel(_("you were not confirming"))
        else:
            self.session.openWithCallback(self.runLabelCallBack, DialogLabelName, _("Select a label(name)"))

    def runLabelCallBack(self, answer):
        print "answer:", answer
        print self.getlabel
        cmd = "e2label %s %s" % (self.getlabel, answer)
        os.system(cmd)
        cmd2 = "blkid | grep %s" % self.getlabel
        print cmd2
        che = os.popen(cmd2)
        check = che.read()
        che.close()
        print check
        if re.search(answer, check):
            self.session.open(MessageBox, _("Labeling succesfull - remounting partition"), type = MessageBox.TYPE_INFO, timeout = 5)
            cmd3 = "umount %s" % self.getlabel
            os.system(cmd3)
            os.system("cd /etc/init.d && ./mountpball")
        else:
            self.session.open(MessageBox, _("Something went wrong - please contact PB-Board"), type = MessageBox.TYPE_INFO, timeout = 5)


    def skipLabel(self,reason):
        self.session.open(MessageBox,_("Labeling was canceled, because %s") % reason, MessageBox.TYPE_ERROR)


    def gettLabel(self):
        getlabel = []
        devs = os.popen("blkid", "r")
        print devs
        for line in devs:
            if "ubifs" not in line:
                iliste = line.split(":")
                inliste = iliste[0]
                h = inliste[4:-1]
                dev = open("/sys/block/%s/device/model" % h, "r").read().strip()
                getlabel.append(( inliste + "   " + dev, "%s" % inliste))
        return getlabel


class DevicesInfo(Screen):
    def __init__(self, session, args = 0):
        self.skin = """
        <screen position="center,center" size="560,400" title="Deviceinfo">
                <widget name="menu" position="0,10" scrollbarMode="showOnDemand" size="560,340"/>
                <ePixmap position="0,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/red_button.png" transparent="1" alphatest="on" />
                <ePixmap position="140,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/green_button.png" transparent="1" alphatest="on" />
                <ePixmap position="280,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/yellow_button.png" transparent="1" alphatest="on" />
                <ePixmap position="420,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/blue_button.png" transparent="1" alphatest="on" />
                <widget name="key_red"    position="0,360"   zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green"  position="140,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_yellow" position="280,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_blue"   position="420,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""
        self.session = session

        Screen.__init__(self, session)
        self.disks = list ()

        self.mdisks = Disks()
        print self.mdisks
        print self.disks
        for disk in self.mdisks.disks:
            print disk
            capacity = "%d MB" % (disk[1] / (1024 * 1024))
            dev = "/dev/%s" % disk[5]
            self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

        self["menu"] = ExtrasList(self.disks)
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button("Info")
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"],
        {
            "green": self.green,
            "red": self.quit,
            "cancel": self.quit,
        }, -2)

    def green(self):
        if len(self.mdisks.disks) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            x = self.mdisks.disks[self.sindex][0]
            print x
            removable = open("/sys/block/%s/removable" % x, "r").read().strip()
            if removable == "1":
                self.session.open(USBInfo, self.mdisks.disks[self.sindex][0])
            else:
                self.session.open(HddInfo, self.mdisks.disks[self.sindex][0])

    def quit(self):
        self.close()



class USBInfo(ConfigListScreen, Screen):
    def __init__(self, session, device):
        self.skin = """
            <screen name="USBInfo" position="center,center" size="600,400" title="Info">
                <widget font="Regular;18" halign="center" name="model" position="0,10" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="manufacturer" position="0,50" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="serial" position="0,90" size="500,25" valign="center" />
                <widget font="Regular;17" halign="center" name="readDisk" position="0,130" size="500,30" valign="center" />
                <widget font="Regular;17" halign="center" name="readCache" position="0,170" size="500,34" valign="center" />
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
        self["model"] = Label("Model: unknow")
        self["manufacturer"] = Label("Manufacturer: unknow")
        self["serial"] = Label("Serial: unknow")
        self["readDisk"] = Label("Read disk speed: unknow")
        self["readCache"] = Label("Read disk cache speed: unknow")
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "red": self.keyCancel,
            "green": self.keySave,
            "cancel": self.keyCancel,
        }, -2)

        self.onLayoutFinish.append(self.drawInfo)

    def drawInfo(self):
        device = "/dev/%s" % self.device
        #regexps
        modelRe = re.compile(r"Model Number:\s*(.*)")
        manufacturerRe = re.compile(r"Manufacturer:\s*([\w\-]+)")
        serialRe = re.compile(r"Serial:\s*([\w\-]+)")
        readDiskRe = re.compile(r"Timing buffered disk reads:\s*(.*)")
        readCacheRe = re.compile(r"cache\s*(.*)")
        if os.path.isfile("/proc/bus/usb/devices"):
            lsmod = os.popen("cat /proc/bus/usb/devices | grep -v OHCI | grep -v EHCI | grep Product | tr -s ' ' ' ' | cut -b 12-")
        else:
            lsmod = os.popen("cd /usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts && ./usb-devices | grep -v OHCI | grep -v EHCI | grep Product | tr -s ' ' ' ' | cut -b 12-")
        model = lsmod.read().strip()
        self["model"].setText("Model: %s" % model)
        lsmod.close()
        if os.path.isfile("/proc/bus/usb/devices"):
            lsmanu = os.popen ("cat /proc/bus/usb/devices | grep -v ohci | grep -v ehci | grep Manufacturer | tr -s ' ' ' ' | cut -b 17-")
        else:
            lsmanu = os.popen ("cd /usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts && ./usb-devices | grep -v ohci | grep -v ehci | grep Manufacturer | tr -s ' ' ' ' | cut -b 17-")
        manufacturer = lsmanu.read().strip()
        self["manufacturer"].setText("Manufacturer: %s" % manufacturer)
        lsmanu.close()
        if os.path.isfile("/proc/bus/usb/devices"):
            lsser = os.popen("cat /proc/bus/usb/devices | grep -v ohci | grep -v ehci | grep Serial | tr -s ' ' ' ' | cut -b 17-")
        else:
            lsser = os.popen("cd /usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts && ./usb-devices | grep -v ohci | grep -v ehci | grep Serial | tr -s ' ' ' ' | cut -b 17-")
        serial = lsser.read().strip()
        self["serial"].setText("Serial: %s" % serial)
        lsser.close()
        hdparm = os.popen("hdparm -t %s" % device)
        for line in hdparm:
            readDisk = re.findall(readDiskRe, line)
            if readDisk:
                self["readDisk"].setText("Read disk speed: %s" % readDisk[0].lstrip())
        hdparm.close()
        hdparm = os.popen("hdparm -T %s" % device)
        for line in hdparm:
            readCache = re.findall(readCacheRe, line)
            if readCache:
                self["readCache"].setText("Read disk cache speed: %s" % readCache[0].lstrip())
        hdparm.close()


class Disks():
    def __init__(self):
        self.disks = []
        self.readDisks()

    def readDisks(self):
        partitions = open("/proc/partitions")
        for part in partitions:
            res = re.sub("\s+", " ", part).strip().split(" ")
            if res and len(res) == 4:
                if len(res[3]) == 3 and (res[3][:2] == "hd" or res[3][:2] == "sd"):
                    self.disks.append([ res[3],
                                        int(res[2]) * 1024,
                                        self.isRemovable(res[3]),
                                        self.getModel(res[3]),
                                        self.getVendor(res[3]),
                                        [ ] ])

    def isRemovable(self, device):
        removable = open("/sys/block/%s/removable" % device, "r").read().strip()
        if removable == "1":
            return True
        return False

    def getModel(self, device):
        if os.access("/sys/block/%s/device/model" % device, os.F_OK):
            return open("/sys/block/%s/device/model" % device, "r").read().strip()
        elif os.access("/proc/ide/%s/model" % device, os.F_OK):
            return open("/proc/ide/%s/model" % device, "r").read().strip()
        else:
            return "unknown or nothing"

    def getVendor(self, device):
        if os.access("/sys/block/%s/device/vendor" % device, os.F_OK):
            return open("/sys/block/%s/device/vendor" % device, "r").read().strip()
        else:
            return "IDE"


def DiskEntry(model, size, removable):
    res = [(model, size, removable)]
    if removable:
        picture = ("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/usbpendrive.png")
    else:
        picture = ("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/hdd.png")

    if fileExists(picture):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(48, 48), png=loadPNG(picture)))
    res.append(MultiContentEntryText(pos=(65, 10), size=(360, 38), font=0, text=model))
    res.append(MultiContentEntryText(pos=(435, 10), size=(125, 38), font=0, text=size))

    return res

class HddInfo(ConfigListScreen, Screen):
    def __init__(self, session, device):
        self.skin = """
            <screen name="HddInfo" position="center,center" size="600,400" title="Info">
                <widget font="Regular;18" halign="center" name="model" position="0,10" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="serial" position="0,40" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="firmware" position="0,70" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="cylinders" position="0,100" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="heads" position="0,130" size="500,25" valign="center" />
                <widget font="Regular;18" halign="center" name="sectors" position="0,160" size="500,25" valign="center" />
                <widget font="Regular;17" halign="center" name="readDisk" position="0,190" size="500,30" valign="center" />
                <widget font="Regular;17" halign="center" name="readCache" position="0,230" size="500,34" valign="center" />
                <widget font="Regular;18" halign="center" name="temp" position="0,260" size="500,25" valign="center" />
                <ePixmap position="70,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/red_button.png" transparent="1" alphatest="on" />
                <ePixmap position="350,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/green_button.png" transparent="1" alphatest="on" />
                <widget name="key_red" position="70,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green" position="350,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
            </screen>"""
        Screen.__init__(self, session)
        self.device = device
        self.list = []

        ConfigListScreen.__init__(self, self.list)

        self["key_green"] = Button("Ok")
        self["key_red"] = Button(_("Exit"))
        self["model"] = Label("Model: unknow")
        self["serial"] = Label("Serial: unknow")
        self["firmware"] = Label("Firmware: unknow")
        self["cylinders"] = Label("Cylinders: unknow")
        self["heads"] = Label("Heads: unknow")
        self["sectors"] = Label("Sectors: unknow")
        self["readDisk"] = Label("Read disk speed: unknow")
        self["readCache"] = Label("Read disk cache speed: unknow")
        self["temp"] = Label("Disk temperature: unknow")
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "red": self.keyCancel,
            "green": self.keySave,
            "cancel": self.keyCancel,
        }, -2)

        self.onLayoutFinish.append(self.drawInfo)

    def drawInfo(self):
        device = "/dev/%s" % self.device
        #regexps
        modelRe = re.compile(r"Model Number:\s*(.*)")
        serialRe = re.compile(r"Serial Number:\s*([\w\-]+)")
        firmwareRe = re.compile(r"Firmware Revision:\s*([\w\-]+)")
        cylindersRe = re.compile(r"cylinders\s*(\d+)\s*(\d+)")
        headsRe = re.compile(r"heads\s*(\d+)\s*(\d+)")
        sectorsRe = re.compile(r"sectors/track\s*(\d+)\s*(\d+)")
        readDiskRe = re.compile(r"Timing buffered disk reads:\s*(.*)")
        readCacheRe = re.compile(r"cache\s*(.*)")
        tempRe = re.compile(r"%s:.*:(.*)" % device)

        # wake up disk... disk in standby may cause not correct value
        os.system("hdparm -S 0 %s" % device)

        hdparm = os.popen("hdparm -I %s" % device)
        for line in hdparm:
            model = re.findall(modelRe, line)
            if model:
                self["model"].setText("Model: %s" % model[0].lstrip())
            serial = re.findall(serialRe, line)
            if serial:
                self["serial"].setText("Serial: %s" % serial[0].lstrip())
            firmware = re.findall(firmwareRe, line)
            if firmware:
                self["firmware"].setText("Firmware: %s" % firmware[0].lstrip())
            cylinders = re.findall(cylindersRe, line)
            if cylinders:
                self["cylinders"].setText("Cylinders: %s (max) %s (current)" % (cylinders[0][0].lstrip(), cylinders[0][1].lstrip()))
            heads = re.findall(headsRe, line)
            if heads:
                self["heads"].setText("Heads: %s (max) %s (current)" % (heads[0][0].lstrip(), heads[0][1].lstrip()))
            sectors = re.findall(sectorsRe, line)
            if sectors:
                self["sectors"].setText("Sectors: %s (max) %s (current)" % (sectors[0][0].lstrip(), sectors[0][1].lstrip()))
        hdparm.close()
        hdparm = os.popen("hdparm -t %s" % device)
        for line in hdparm:
            readDisk = re.findall(readDiskRe, line)
            if readDisk:
                self["readDisk"].setText("Read disk speed: %s" % readDisk[0].lstrip())
        hdparm.close()
        hdparm = os.popen("hdparm -T %s" % device)
        for line in hdparm:
            readCache = re.findall(readCacheRe, line)
            if readCache:
                self["readCache"].setText("Read disk cache speed: %s" % readCache[0].lstrip())
        hdparm.close()
        hddtemp = os.popen("/usr/sbin/hddtemp -q %s" % device)
        for line in hddtemp:
            temp = re.findall(tempRe, line)
            if temp:
                self["temp"].setText("Disk temperature: %s" % temp[0].lstrip())
        hddtemp.close()

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


class DialogLabelName(Screen):

        skin = """
                <screen name="DialogLabelName" position="60,245" size="600,10" title="Powerboardcenter">
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
                self.list.append("usb")
                self.list.append("usb1")
                self.list.append("usb2")
                self.list.append("usb3")
                self.list.append("cf")
                self.list.append("hdd")
                self.list.append("hdd1")
                self.list.append("hdd2")
                self.list.append("hdd3")
                self.list.append("mmc1")
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
                
###########################################################################