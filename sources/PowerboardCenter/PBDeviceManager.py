#'''
#Created on 14.11.2011
#Edited 13.04.2014 by graugans
# 29.11.2014 Added interaction with E2 Harddiskmanager - add/remove mounted partitions - tom
# 1.12.2014 Added ext4 support - tom
# 7.12.2014 fixed some special cases like bad disk or no partitions at all
#Edited by Franc 25.05.2016 - Skin stuff
#@author: terrajoe based on openee-code
#'''
##########################################################
# -*- coding: utf-8 -*-

Estuary = "/usr/share/enigma2/Estuary/"

from __init__ import _
from enigma import *
from Components.ConfigList import *
from Components.config import *
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.NetworkSetup import AdapterSetup
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Components.Harddisk import harddiskmanager, Harddisk, isFileSystemSupported
from Tools.Directories import fileExists, crawlDirectory, resolveFilename, SCOPE_ACTIVE_SKIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens import HarddiskSetup
from enigma import eSize, ePoint
from Components.Sources.StaticText import StaticText

import os
import sys
import re
import string
import shutil
import time
import subprocess


def isFSSupported(filesystem):
    try:
        file = open('/proc/filesystems', 'r')
        for fs in file:
            if fs.strip().endswith(filesystem):
                file.close()
                return True
        file.close()
        return False
    except Exception, ex:
        print "[PB DM] Failed to read /proc/filesystems:", ex


def getKernelVer(self):
    try:
        file = open("/proc/version","r")
        version = map(int, file.read().split(' ', 4)[2].split('.',2)[:2])
        file.close()
        print "[PB DM] Linux version:", version # returns e.g. [3, 13]
        return version
#            if (version[0] > 3) or (version[0] > 2 and version[1] >= 2):
# Linux version 3.2 supports bigalloc and -C option, use 256k blocks
    except Exception, ex:
        print "[PB DM] Failed to detect Linux version:", ex

#### USBInfo
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
        boxinfo = BoxInfo()
        boxinfo.detectBox()
        self.device = device
        self.list = []

        ConfigListScreen.__init__(self, self.list)

        self["key_green"] = Button("OK")
        self["key_red"] = Button(_("Exit"))
        self["model"] = Label("Model: unknown")
        self["manufacturer"] = Label("Manufacturer: unknown")
        self["serial"] = Label("Serial: unknown")
        self["readDisk"] = Label("Read disk speed: unknown")
        self["readCache"] = Label("Read disk cache speed: unknown")
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

#### HddInfo
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
        boxinfo = BoxInfo()
        boxinfo.detectBox()
        self.device = device
        self.list = []

        ConfigListScreen.__init__(self, self.list)

        self["key_green"] = Button("Ok")
        self["key_red"] = Button(_("Exit"))
        self["model"] = Label("Model: unknown")
        self["serial"] = Label("Serial: unknown")
        self["firmware"] = Label("Firmware: unknown")
        self["cylinders"] = Label("Cylinders: unknown")
        self["heads"] = Label("Heads: unknown")
        self["sectors"] = Label("Sectors: unknown")
        self["readDisk"] = Label("Read disk speed: unknown")
        self["readCache"] = Label("Read disk cache speed: unknown")
        self["temp"] = Label("Disk temperature: unknown")
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
## get raw speed
        hdparm = os.popen("hdparm -t %s" % device)
        for line in hdparm:
            readDisk = re.findall(readDiskRe, line)
            if readDisk:
                self["readDisk"].setText("Read disk speed: %s" % readDisk[0].lstrip())
        hdparm.close()
## get cached speed
        hdparm = os.popen("hdparm -T %s" % device)
        for line in hdparm:
            readCache = re.findall(readCacheRe, line)
            if readCache:
                self["readCache"].setText("Read disk cache speed: %s" % readCache[0].lstrip())
        hdparm.close()
## get temp speed
        hddtemp = os.popen("/usr/sbin/hddtemp -q %s" % device)
        for line in hddtemp:
            temp = re.findall(tempRe, line)
            if temp:
                self["temp"].setText("Disk temperature: %s" % temp[0].lstrip())
        hddtemp.close()
#############
#### HddMount
class HddMount(Screen):
    def __init__(self, session, device, partition):
        self.skin = """
            <screen name="HddMount" position="center,center" size="560,400" title="Mounts">
                <widget name="menu" position="10,10" scrollbarMode="showOnDemand" size="540,320"/>
                <ePixmap position="0,360"   zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/red_button.png" transparent="1" alphatest="on" />
                <ePixmap position="140,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/green_button.png" transparent="1" alphatest="on" />
                <ePixmap position="280,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/yellow_button.png" transparent="1" alphatest="on" />
                <ePixmap position="420,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/blue_button.png" transparent="1" alphatest="on" />
                <widget name="key_red"    position="0,360"   zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green"  position="140,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_yellow" position="280,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_blue"   position="420,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
            </screen>"""
        Screen.__init__(self, session)

        self.device = device
        self.partition = partition
        self.mountpoints = MountPoints()
        self.mountpoints.read()

        self.list = []
        self.list.append("Mount as /media/hdd")
        self.list.append("Mount as /media/hdd1")
        self.list.append("Mount as /media/hdd2")
        self.list.append("Mount as /media/hdd3")
        self.list.append("Mount as /media/usb")
        self.list.append("Mount as /media/usb1")
        self.list.append("Mount as /media/usb2")
        self.list.append("Mount as /media/usb3")
        self.list.append("Mount as /media/cf")
        self.list.append("Mount as /media/mmc1")
        self.list.append("Mount on custom path")

        self["menu"] = MenuList(self.list)

        self["key_green"] = Button("")
        self["key_red"] = Button(_("Ok"))
        self["key_blue"] = Button(_("Exit"))
        self["key_yellow"] = Button("")
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "blue": self.quit,
            #"yellow": self.yellow,
            "red": self.ok,
            "ok": self.ok,
            "cancel": self.quit,
        }, -2)

    def ok(self):
        selected = self["menu"].getSelectedIndex()
        if selected == 0:
            self.setMountPoint("/media/hdd")
        elif selected == 1:
            self.setMountPoint("/media/hdd1")
        elif selected == 2:
            self.setMountPoint("/media/hdd2")
        elif selected == 3:
            self.setMountPoint("/media/hdd3")
        elif selected == 4:
            self.setMountPoint("/media/usb")
        elif selected == 5:
            self.setMountPoint("/media/usb1")
        elif selected == 6:
            self.setMountPoint("/media/usb2")
        elif selected == 7:
            self.setMountPoint("/media/usb3")
        elif selected == 8:
            self.setMountPoint("/media/cf")
        elif selected == 9:
            self.setMountPoint("/media/mmc1")
        elif selected == 10:
            self.session.openWithCallback(self.customPath, VirtualKeyBoard, title = (_("Insert mount point:")), text = "/media/custom")

    def customPath(self, result):
        if result and len(result) > 0:
            result = result.rstrip("/")
            os.system("mkdir -p %s" % result)
            self.setMountPoint(result)

    def setMountPoint(self, path):
        self.cpath = path
        if self.mountpoints.exist(path):
            self.session.openWithCallback(self.setMountPointCb, ExtraMessageBox, "Selected mount point is already used by another drive.", "Mount point exist!",
                                                                [ [ "Change old drive with this new drive", "ok.png" ],
                                                                    [ "Mantain old drive", "cancel.png" ],
                                                                    ])
        else:
            self.setMountPointCb(0)

    def setMountPointCb(self, result):
        if result == 0:
            if self.mountpoints.isMounted(self.cpath):
                if not self.mountpoints.umount(self.cpath):
                    self.session.open(MessageBox, _("Cannot umount current drive. Timeshift, recording or some external tools (like samba and nfsd) may cause this problem. Please stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
                    self.close()
                    return
            self.mountpoints.delete(self.cpath)
            self.mountpoints.add(self.device, self.partition, self.cpath)
            self.mountpoints.write()
            if not self.mountpoints.mount(self.device, self.partition, self.cpath):
                self.session.open(MessageBox, _("Cannot mount new drive. Please check filesystem or format it and try again"), MessageBox.TYPE_ERROR)
            elif self.cpath == "/media/hdd":
                os.system("/bin/mkdir /hdd/movie")
            self.close()

    def quit(self):
        self.close()

### PartitionEntry
def PartitionEntry(description, size):
    res = [(description, size)]
    picture = ("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/partitionmanager.png")
    if fileExists(picture):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(48, 48), png=loadPNG(picture)))
    # Estuary - Start Here
    if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
        res.append(MultiContentEntryText(pos=(65, 5), size=(935, 38), font=0, text=description))
        res.append(MultiContentEntryText(pos=(936, 5), size=(285, 38), font=0, flags = RT_HALIGN_RIGHT, text=size))
    else:
    # Estuary - End Here
        res.append(MultiContentEntryText(pos=(65, 10), size=(360, 38), font=0, text=description))
        res.append(MultiContentEntryText(pos=(435, 10), size=(125, 38), font=0, text=size))
    return res

#### HddPartitions
class HddPartitions(Screen):
    def __init__(self, session, disk):
        self.skin = """
            <screen name="HddPartitions" position="center,center" size="560,400" title="Partitions">
                <widget name="menu" position="0,10" scrollbarMode="showOnDemand" size="560,340"/>
                <ePixmap position="0,360"   zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/red_button.png" transparent="1" alphatest="on" />
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
        self.disk = disk
#        print "[oo PB HddPartitions before refreshMP]"
        self.refreshMP(False)
#        print "[oo PB HddPartitions after refreshMP]"
#        print "[oo PB HddPartitions self.partitions]", self.partitions
        if self.partitions == []:
                self.partitions.append(PartitionEntry("No partitions found.", "Initialze first."))
        self["menu"] = ExtrasList(self.partitions)
        self["menu"].onSelectionChanged.append(self.selectionChanged)
        self["key_red"] = Button("")
        self["key_green"] = Button("")
        self["key_yellow"] = Button("")
        self["key_blue"] = Button(_("Exit"))
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "blue": self.quit,
            "yellow": self.yellow,
            "green": self.green,
            "red": self.red,
            "cancel": self.quit,
        }, -2)

## remove
#        print "[oo PB HddPartitions self.disk - ]", self.disk
#        print "[oo PB HddPartitions self.disk5 - ]", self.disk[5]
        if len(self.disk[5]) > 0:
            self["key_green"].setText(_("Check"))
            self["key_yellow"].setText(_("Format"))
            if self.disk[5][0][2] == "Linux swap":  ### next 10 lines were tabbed in - failed on a bad disk as disk[5] = []
                self["key_red"].setText("")
            else:
                mp = self.mountpoints.get(self.disk[0], "1")
                if len(mp) > 0:
                    self.mounted = True
                    self["key_red"].setText(_("Unmount"))
                else:
                    self.mounted = False
                    self["key_red"].setText(_("Mount"))

    def selectionChanged(self):
        self["key_green"].setText("")
        self["key_yellow"].setText("")
        if len(self.disk[5]) > 0:
            part = self["menu"].l.getCurrentSelection()
            a = part[0]
            b = a[0]
            partnum = b.split(" ")
            self["key_green"].setText(_("Check"))
            self["key_yellow"].setText(_("Format"))

            if partnum[3] == "Linux swap":
                self["key_red"].setText("")
            else:
                mp = self.mountpoints.get(self.disk[0], partnum[1])
                if len(mp) > 0:
                    self.mounted = True
                    self["key_red"].setText(_("Unmount"))
                else:
                    self.mounted = False
                    self["key_red"].setText(_("Mount"))

    def chkfs(self):
        disks = Disks()
        ret = disks.chkfs(self.disk[5][self.index][0][:3], self.partnum)
        if ret == 0:
            self.session.open(MessageBox, _("Check disk terminated with success!"), MessageBox.TYPE_INFO)
        elif ret == -1:
            self.session.open(MessageBox, _("Cannot umount current drive. A record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem. Please stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _("Error checking disk. The disk may be damaged"), MessageBox.TYPE_ERROR)

    def mkext2(self):
        disks = Disks()
        ret = disks.mkfs2(self.disk[5][self.index][0][:3], self.partnum)
        if ret == 0:
            self.session.open(MessageBox, _("Format terminated with success!"), MessageBox.TYPE_INFO)
        elif ret == -2:
            self.session.open(MessageBox, _("Cannot format current drive. A record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem. Please stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _("Error formatting disk. The disk may be damaged"), MessageBox.TYPE_ERROR)
        self.refreshMP()

    def mkext3(self):
        disks = Disks()
        ret = disks.mkfs3(self.disk[5][self.index][0][:3], self.partnum)
        if ret == 0:
            self.session.open(MessageBox, _("Format terminated with success!"), MessageBox.TYPE_INFO)
        elif ret == -2:
            self.session.open(MessageBox, _("Cannot format current drive. A record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem. Please stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _("Error formatting disk. The disk may be damaged"), MessageBox.TYPE_ERROR)
        self.refreshMP()

    def mkext4(self):
        disks = Disks()
        ret = disks.mkfs4(self.disk[5][self.index][0][:3], self.partnum)
        if ret == 0:
            self.session.open(MessageBox, _("Format terminated with success!"), MessageBox.TYPE_INFO)
        elif ret == -2:
            self.session.open(MessageBox, _("Cannot format current drive. A record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem. Please stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _("Error formatting disk. The disk may be damaged"), MessageBox.TYPE_ERROR)
        self.refreshMP()

    def mkvfat(self):
        disks = Disks()
        ret = disks.mkfsvfat(self.disk[5][self.index][0][:3], self.partnum)
        if ret == 0:
            self.session.open(MessageBox, _("Format terminated with success!"), MessageBox.TYPE_INFO)
        elif ret == -2:
            self.session.open(MessageBox, _("Cannot format current drive. A record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem. Please stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _("Error formatting disk. The disk may be damaged"), MessageBox.TYPE_ERROR)
        self.refreshMP()

### CHKDSK
    def green(self):
        if len(self.disk[5]) > 0:
            index = self["menu"].getSelectionIndex()
            part = self["menu"].l.getCurrentSelection()
            a = part[0]
            b = a[0]
            c = b.split(" ")
            partnum = int(c[1])
            self.index = index
            self.partnum = partnum
            self.session.open(ExtraActionBox, "Checking disk %s" % self.disk[5][index][0], "Checking disk", self.chkfs)

### Format: 
    def yellow(self):
        if len(self.disk[5]) > 0:
            index = self["menu"].getSelectionIndex()
            part = self["menu"].l.getCurrentSelection()
            a = part[0]
            b = a[0]
            c = b.split(" ")
            partnum = int(c[1])
            self.index = index
            self.partnum = partnum
            self.session.openWithCallback(self.runFormatCallBack, DialogFormat, _("Select filesystem for formatting"))
            self.refreshMP()

    def runFormatCallBack(self, answer):
        print "answer:", answer
        if answer == 0:
            self.session.open(ExtraActionBox, "Formatting, please wait...", "Formatting disk - ext2", self.mkext2)
        elif answer == 1:
            self.session.open(ExtraActionBox, "Formatting, please wait...", "Formatting disk - ext3", self.mkext3)
        elif answer == 2:
            self.session.open(ExtraActionBox, "Formatting, please wait...", "Formatting disk - FAT32", self.mkvfat)
        elif answer == 3:
            self.session.open(ExtraActionBox, "Formatting, please wait...", "Formatting disk - ext4", self.mkext4)
        self.refreshMP()

    def refreshMP(self, uirefresh = True):
        self.partitions = []
        self.mountpoints = MountPoints()
        self.mountpoints.read()
        for part in self.disk[5]:
# use python 2.7 to put commas in MB size
            capacity = "{:,d} MB".format(part[1] / (1024 * 1024))
#            capacity = "%d MB" % (part[1] / (1024 * 1024))
            mp = self.mountpoints.get(self.disk[0], part[0][3])
            helper = "/dev/" + self.disk[0]
            helper2 = helper + str(part[0][3])
            helper3 = "fdisk -l " + helper + " | grep " + helper2
            partid1 = os.popen(helper3)
            partid2 = partid1.read().strip()
            partid3 = " ".join(partid2.split())
            partid = partid3.split(" ")
            partid1.close()
#            print "[PB HddPartitions] partid ", partid
            if "W95" in partid:
                partitionid = "FAT32"
            elif "Linux" in partid:
                partitionid = "Linux"
#            elif "HPFS" in partid:
#                partitionid = "NTFS/HPFS"
            else:
                partitionid = "Win/OsX" # partid[6] - not enough space for display - fixit and used partid[6]    # was partid[5] - raw partid, not desciption
#### TODO: 
# Check for more kernel version - big fun, like for info()
# if linux 3.13 shows 83
#            else:
#                kv = getKernelVer(self)
#                    if (kv[0] > 3 and kv[1] > 11):
#                        partitionid = partid[6]
# if linux 3.13 shows Linux
#                    else:
#                        partitionid = partid[5]
            if (len(mp) > 0):
                self.partitions.append(PartitionEntry("Partition %s - %s (%s)       " % (part[0][3], partitionid, mp), capacity))
            else:
                self.partitions.append(PartitionEntry("Partition %s - %s        " % (part[0][3], partitionid), capacity))
        if uirefresh:
            self["menu"].setList(self.partitions)

    def red(self):
        if len(self.disk[5]) > 0:
            index = self["menu"].l.getCurrentSelection()
            a = index[0]
            b = a[0]
            partnum = b.split(" ")
            if partnum[3] == "Linux swap":
                return

        if len(self.partitions) > 0:
            self.sindex = self['menu'].l.getCurrentSelection()
            a = self.sindex[0]
            b = a[0]
            partnum = b.split(" ")
            helper = "/dev/" + self.disk[0]
            helper2 = helper + str(partnum[1])
            helper3 = "fdisk -l " + helper + " | grep " + helper2
            partid1 = os.popen(helper3)
            partid2 = partid1.read().strip()
            partid3 = " ".join(partid2.split())
            partid = partid3.split(" ")
            partid1.close()
            if "FAT16" in partid:
                self.session.open(MessageBox, _("FAT16 on a partition detected, please format it or initialise device!"), MessageBox.TYPE_ERROR)
            else:
                if self.mounted:
                    mp = self.mountpoints.get(self.disk[0], partnum[1])
                    if len(mp) > 0:
                        if self.mountpoints.isMounted(mp):
                            if self.mountpoints.umount(mp):
                                self.mountpoints.delete(mp)
                                self.mountpoints.write()
                            else:
                                self.session.open(MessageBox, _("Cannot umount device. A record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem. Please stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
                        else:
                            self.mountpoints.delete(mp)
                            self.mountpoints.write()

                    self.refreshMP()
                else:
                    self.session.openWithCallback(self.refreshMP, HddMount, self.disk[0], partnum[1])

    def quit(self):
        self.close()

#### Expander 
class Expander(Screen):
    def __init__(self, session, disk):
        self.skin = """
            <screen name="Expander" position="center,center" size="560,400" title="Flash-Expander">
                <widget name="menu" position="0,10" scrollbarMode="showOnDemand" size="560,340"/>
                <ePixmap position="0,345" zPosition="1" size="280,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/expand_green.png" transparent="1" alphatest="on" />
                <ePixmap position="280,345" zPosition="1" size="280,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/expand_yellow.png" transparent="1" alphatest="on" />
                <widget name="key_green"  position="0,345" zPosition="2" size="280,50" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_yellow" position="280,345" zPosition="2" size="280,50" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
            </screen>"""
        self.session = session

        Screen.__init__(self, session)
        self.disk = disk
        self.refreshMP(False)

        self["menu"] = ExtrasList(self.partitions)
        self["key_green"] = Button(_("Expand to device"))
        self["key_yellow"] = Button(_("Get rid of expand"))
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "yellow": self.yellow,
            "green": self.green,
            "cancel": self.quit,
        }, -2)

    def ausl(self):
        disks = Disks()
        ret = disks.ausl(self.disk[5][self.index][0][:3], self.partnum)
        if ret == 0:
            self.session.open(MessageBox, _("Expanding ready! Restarting box NOW"), MessageBox.TYPE_INFO)
            time.sleep(5)
            os.system("reboot -nf")
        elif ret == 1:
            self.session.open(MessageBox, _("Device not mountet - please mount as something"), MessageBox.TYPE_ERROR)
        elif ret == 2:
            self.session.open(MessageBox, _("No EXT2- or EXT3-filesystem! Please format the device."), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _("Error"), MessageBox.TYPE_ERROR)

    def raus(self):
        disks = Disks()
        ret = disks.raus(self.disk[5][self.index][0][:3], self.partnum)
        if ret == 0:
            self.session.open(MessageBox, _("Back in flash again! Restarting box NOW"), MessageBox.TYPE_INFO)
            time.sleep(5)
            os.system("reboot -nf")
        else:
            self.session.open(MessageBox, _("Error"), MessageBox.TYPE_ERROR)

    def green(self):
        if len(self.disk[5]) > 0:
            index = self["menu"].getSelectionIndex()
            part = self["menu"].l.getCurrentSelection()
            a = part[0]
            b = a[0]
            c = b.split(" ")
            partnum = int(c[1])
            if self.disk[5][index][2] == "Linux":
                self.index = index
                self.partnum = partnum
                self.session.open(ExtraActionBox, "Expanding to device... This could take some time! Box will be restarted when finished!", "Expanding to device", self.ausl)

    def yellow(self):
        if len(self.disk[5]) > 0:
            index = self["menu"].getSelectionIndex()
            part = self["menu"].l.getCurrentSelection()
            a = part[0]
            b = a[0]
            c = b.split(" ")
            partnum = int(c[1])
            if self.disk[5][index][2] == "Linux":
                self.index = index
                self.partnum = partnum
                self.session.open(ExtraActionBox, "Getting rid of entries and mounts. This could take some Time! Box will be restarted when finished!", "Get rid of outsource", self.raus)

    def refreshMP(self, uirefresh = True):
        self.partitions = []
        self.mountpoints = MountPoints()
        self.mountpoints.read()
        for part in self.disk[5]:
# use python 2.7 to put commas in MB size
            capacity = "{:,d} MB".format(part[1] / (1024 * 1024))
#            capacity = "%d MB" % (part[1] / (1024 * 1024))
            mp = self.mountpoints.get(self.disk[0], part[0][3])
            if len(mp) > 0:
                self.partitions.append(PartitionEntry("Partition %s - %s (%s)       " % (part[0][3], part[2], mp), capacity))
            else:
                self.partitions.append(PartitionEntry("Partition %s - %s        " % (part[0][3], part[2]), capacity))

        if uirefresh:
            self["menu"].setList(self.partitions)

    def quit(self):
        self.close()

def DiskEntry(model, size, removable):
    res = [(model, size, removable)]
    if removable:
        picture = ("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/usbpendrive.png")
    else:
        picture = ("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/hdd.png")

    if fileExists(picture):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(48, 48), png=loadPNG(picture)))
        # Estuary - Start Here
    if resolveFilename(SCOPE_ACTIVE_SKIN) == Estuary:
        res.append(MultiContentEntryText(pos=(65, 5), size=(935, 38), font=0, text=model))
        res.append(MultiContentEntryText(pos=(936, 5), size=(285, 38), font=0, flags = RT_HALIGN_RIGHT, text=size))
    else:
    # Estuary - End Here
        res.append(MultiContentEntryText(pos=(65, 10), size=(360, 38), font=0, text=model))
        res.append(MultiContentEntryText(pos=(435, 10), size=(125, 38), font=0, text=size))
    return res



#### HddSetup 
class HddSetup(Screen):
    def __init__(self, session, args = 0):
        self.skin = """
        <screen position="center,center" size="560,400" title="Device Setup">
                <widget name="menu" position="0,10" scrollbarMode="showOnDemand" size="560,340"/>
                <ePixmap position="0,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/red_button.png" transparent="1" alphatest="on" />
                <ePixmap position="140,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/green_button.png" transparent="1" alphatest="on" />
                <ePixmap position="280,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/yellow_button.png" transparent="1" alphatest="on" />
                <ePixmap position="420,360" zPosition="1" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/blue_button.png" transparent="1" alphatest="on" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/menu.png" alphatest="on" position="10,320" size="70,30" transparent="1" />
                <widget name="key_red"    position="0,360"   zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green"  position="140,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_yellow" position="280,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_blue"   position="420,360" zPosition="2" size="140,40" halign="center" valign="center" font="Regular;22" transparent="1" backgroundColor="black" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""
        self.session = session

        Screen.__init__(self, session)
        self.disks = list ()

        self.mdisks = Disks()
#        print "[-- PB HddSetup] self.mdisks", self.mdisks 
        for disk in self.mdisks.disks:   # for all attached disks
#            print "[-- PB HddSetup] disk[0]", disk[0]   # device physical /sda /sdb ..
#            print "[-- PB HddSetup] disk[1]", disk[1]   # size bytes
#            print "[-- PB HddSetup] disk[2]", disk[2]   # boolean True/False isRemovable?
#            print "[-- PB HddSetup] disk[3]", disk[3]   # name eg. SAMSUNG HM641JI or Silicon-Power16G
#            print "[-- PB HddSetup] disk[5]", disk[4]   # interface for USB-UFD 2.0 for eSATA-ATA
# use python 2.7 to put commas in MB size
            capacity = "{:,d} MB".format(disk[1] / (1024 * 1024))
#            capacity = "%d MB" % (disk[1] / (1024 * 1024))
            self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

        self["menu"] = ExtrasList(self.disks)
        self["key_red"] = Button(_("Partitions"))
        self["key_green"] = Button("Info")
        self["key_yellow"] = Button(_("Initialize"))
        self["key_blue"] = Button(_("Swapfile"))
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"],
        {
            "blue": self.startSwap,
            "yellow": self.yellow,
            "green": self.green,
            "red": self.red,
            "cancel": self.quit,
            "menu": self.expander,
        }, -2)

    def yellow(self):
        if len(self.mdisks.disks) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            if os.path.isfile("/usr/sbin/parted"):
                self.session.openWithCallback(self.initialaze, ExtraMessageBox, "Please select your preferred configuration.", "HDD Partitioner",
                                        [ [ "One partition", "partitionmanager.png" ],
                                        [ "Two partitions (50% - 50%)", "partitionmanager.png" ],
                                        [ "Two partitions (25% - 75%)", "partitionmanager.png" ],
                                        [ "Two partitions (10% - 90%)", "partitionmanager.png" ],
                                        [ "Two partitions (3% - 97%)", "partitionmanager.png" ],
                                        [ "Two partitions (1% - 99%)", "partitionmanager.png" ],
                                        [ "Cancel", "cancel.png" ],
                                        ], 1, 6)
                self.refresh()
            else:
                self.session.open(MessageBox, _("parted is missing - installing it now"), type = MessageBox.TYPE_INFO, timeout = 30)
                os.system("opkg update")
                os.system("opkg install parted")

    def green(self):
        if len(self.mdisks.disks) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            x = self.mdisks.disks[self.sindex][0]
            print "[PB HddSetup] mounted disks x", x
            removable = open("/sys/block/%s/removable" % x, "r").read().strip()
            if removable == "1":
                self.session.open(USBInfo, self.mdisks.disks[self.sindex][0])
            else:
                self.session.open(HddInfo, self.mdisks.disks[self.sindex][0])

    def red(self):
        if len(self.mdisks.disks) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            self.session.open(HddPartitions, self.mdisks.disks[self.sindex])
            self.refresh()

    def expander(self):
        if len(self.mdisks.disks) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            if os.path.isfile("/usr/bin/rsync"):
                self.session.open(Expander, self.mdisks.disks[self.sindex])
            else:
                self.session.open(MessageBox, _("rsync is missing - installing it now"), type = MessageBox.TYPE_INFO, timeout = 30)
                os.system("opkg update")
                os.system("opkg install rsync")

    def startSwap(self):
        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/swap.py"):
#was            from Plugins.Extensions.PowerboardCenter.swap import *
            from Plugins.Extensions.PowerboardCenter.swap import Swap
            self.session.open(Swap)
        elif fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/swap.pyo"):
#was            from Plugins.Extensions.PowerboardCenter.swap import *
            from Plugins.Extensions.PowerboardCenter.swap import Swap
            self.session.open(Swap)
        else:
            self.session.open(MessageBox, text = _('No Swapmanager installed!'), type = MessageBox.TYPE_ERROR)

    def mkfs(self):
        self.formatted += 1
        return self.mdisks.mkfs(self.mdisks.disks[self.sindex][0], self.formatted)

    def refresh(self):
        self.disks = list ()

        self.mdisks = Disks()
        for disk in self.mdisks.disks:
            print "[PB HddSetup] disk", disk
#            print disk[3]
#            print disk[2]
# use python 2.7 to put commas in MB size
            capacity = "{:,d} MB".format(disk[1] / (1024 * 1024))
#            capacity = "%d MB" % (disk[1] / (1024 * 1024))
            self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

        self["menu"].setList(self.disks)

    def fdiskEnded(self, result):
        if result == 0:
            self.session.open(MessageBox, _("Partitioning done - please format the partitions in the format you want!"), MessageBox.TYPE_INFO)
        elif result == -1:
            self.session.open(MessageBox, _("Cannot umount device. A record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem. Please stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
        elif result == -3:
# dd failed disk bad
            self.session.open(MessageBox, _("Partitioning failed!  Serious disk I/O error."), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _("Partitioning failed!"), MessageBox.TYPE_ERROR)
        self.refresh()

    def fdisk(self):
        return self.mdisks.fdisk(self.mdisks.disks[self.sindex][0], self.mdisks.disks[self.sindex][1], self.result)
        self.refresh()

    def initialaze(self, result):
        if result != 6:
            self.result = result
            self.formatted = 0
            mp = MountPoints()
            mp.read()
            mp.deleteDisk(self.mdisks.disks[self.sindex][0])
            mp.write()
            self.session.openWithCallback(self.fdiskEnded, ExtraActionBox, "Partitioning...", "Initialize disk", self.fdisk)
            self.refresh()

    def quit(self):
        self.close()

############################ Disks #############################
class Disks():
    def __init__(self):
        self.disks = []
        self.readDisks()
        self.readPartitions()
### remove
        getKernelVer(self)

    def readDisks(self):
        partitions = open("/proc/partitions")
        for part in partitions:
            res = re.sub("\s+", " ", part).strip().split(" ")
#            print "[--** PB Disks] readDisks res", res 
            if res and len(res) == 4:
                if len(res[3]) == 3 and (res[3][:2] == "hd" or res[3][:2] == "sd"):
                    self.disks.append([ res[3],
                                        int(res[2]) * 1024,
                                        self.isRemovable(res[3]),
                                        self.getModel(res[3]),
                                        self.getVendor(res[3]),
                                        [ ] ])

    def readPartitions(self):
        partitions = open("/proc/partitions")
        for part in partitions:
            res = re.sub("\s+", " ", part).strip().split(" ")
#            print "[--** PB Disks] readPartitions res", res
            if res and len(res) == 4:
                if len(res[3]) > 3 and ((res[3][:3] == "hdb" or res[3][:2] == "sd" or res[3][:4] == "hda5") and not self.isLinux(res[3]) == "Extended"):
                    for i in self.disks:
                        if i[0] == res[3][:3]:
                            i[5].append([ res[3], int(res[2]) * 1024, self.isLinux(res[3]) ])
                            break
#TODO:
# if Removable/nand based:
# vfat- dirsync,noatime,nodiratime    others- noatime or relatime tune2fs
# alignment @ 4MB
# journaling forbidden - tune2fs -O ^has_journal /dev/sda1 - OK DONE
# ownership to all :
# will not help but chown nobody:nogroup /mnt/externalDrive. chmod 777 /mnt/externalDrive, setfacl N/A 
# tune2fs -l /dev/sdaX | grep features
    def isRemovable(self, device):
        removable = open("/sys/block/%s/removable" % device, "r").read().strip()
        if removable == "1":
#            print "[PB Disks] isRemovable: True"
            return True
#        print "[PB Disks] isRemovable: False"
        return False

# TODO:
#### fix checking for BAD disk !!! switch to subprocess or get stderr
## about errors: besides bad disks, some boxes report errors on mtd like: sfdisk: read error on /dev/mtdblock3 - cannot read sector 0
## so popen4 (STDOUT + STDERR) will fail
# sfdisk is picky with USBs and CHS , fdisk fails (does not scan other disks) if one disk is bad!!!
# in this case device is full device with slice number... for example sda1
    def isLinux(self, device):
#        if os.path.isfile("/sbin/fdisk"):
#            cmd = "/sbin/fdisk -l | grep \"/dev/%s\" | sed s/\*// | awk '{ print $6 \" \" $7 \" \" $8 }'" % device
#        else:
#            cmd = "/usr/sbin/sfdisk -l | grep \"/dev/%s\" | sed s/\*// | awk '{ print $6 \" \" $7 \" \" $8 }'" % device
        cmd = "/usr/sbin/sfdisk -l /dev/%s | grep \"/dev/%s\" " % (device[:-1],  device)       # make it more responsive and do not list ALL the disks
#        print "[------PB Disks] islinux cmd is: ", cmd
#        cmd = "/usr/sbin/sfdisk -l | grep \"/dev/%s\" " % device
        (dummystdin, fdisk) = os.popen4(cmd, "r")
        res = fdisk.read().strip()
        fdisk.close()
#        print "[------PB Disks] islinux device is: ", device
#        print "[------PB Disks] islinux sfdisk output res: ", res
        if 'Linux' in res:
            rres = 'Linux'
        elif 'Extended' in res:
            rres = 'Extended'
        elif 'error' in res:
            rres = 'Error'
        elif 'FAT32' in res:
            rres = 'FAT32'
        else:
            rres = 'Win/OsX'
#            rres = 'W95 FAT32'
#        print "[PB Disks] islinux PARITITON res: ", rres
        return rres

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

    def getSizeInBytes(self, device):
        block_size = 512 #default om most systems
        size = 0
        if os.access("/sys/block/%s/size" % device, os.F_OK):
            try:
                block_size = int(open("/sys/block/%s/queue/logical_block_size" % device, "r").read().strip())
            except:
#                print "[PB Disks] Failed to read blocksize using default of 512"
                block_size = 512
            size = int(open("/sys/block/%s/size" % device, "r").read().strip()) * block_size
        else:
            size = 0
        return size

    def isMounted(self, device):
        mounts = open("/proc/mounts")
        for mount in mounts:
            res = mount.split(" ")
            if res and len(res) > 1:
                if res[0][:8] == "/dev/%s" % device:
                    mounts.close()
                    return True
        mounts.close()
        return False

    def isMountedP(self, device, partition):
        mounts = open("/proc/mounts")
        for mount in mounts:
            res = mount.split(" ")
            if res and len(res) > 1:
                if res[0][:9] == "/dev/%s%s" % (device, partition):
                    mounts.close()
                    return True
        mounts.close()
        return False

    def getMountedP(self, device, partition):
        mounts = open("/proc/mounts")
        for mount in mounts:
            res = mount.split(" ")
            if res and len(res) > 1:
                if res[0] == "/dev/%s%d" % (device, partition):
                    mounts.close()
                    return res[1]
        mounts.close()
        return None

    def umount(self, device):
        mounts = open("/proc/mounts")
        for mount in mounts:
            res = mount.split(" ")
            if res and len(res) > 1:
                if res[0][:8] == "/dev/%s" % device:
#                    print "[PB Disks] umount %s" % res[0]
                    if os.system("umount %s" % res[0]) != 0:
                        mounts.close()
                        return False
        mounts.close()
        return True

    def umountP(self, device, partition):
        if os.system("umount /dev/%s%d" % (device, partition)) != 0:
            return False
        return True

    def mountP(self, device, partition, path):
        if os.system("mount /dev/%s%d %s" % (device, partition, path)) != 0:
            return False
        return True

    def mount(self, fdevice, path):
        if os.system("mount /dev/%s %s" % (fdevice, path)) != 0:
            return False
        return True

    # type:
    # 0 -> one partition
    # 1 -> two partition (2 x 50%)
    # 2 -> two partition (25% 75%)
    # 3 -> two partition (10% x 90%)
    # 4 -> two partition (3% x 97%)
    # 5 -> two partition (1% x 99%)
    #
    # return value:
    # 0 -> ok
    # -1 -> umount failed
    # -2 -> parted failed
    # -3 -> dd failed i/o error
    def fdisk(self, device, size, type):
        print "[PB Disks] partitioning device %s" % device
        if self.isMounted(device):
#            print "[PB Disks] device is mounted... umount"
            if not self.umount(device):
#                print "[PB Disks] umount failed!"
                return -1
        dsiz = self.getSizeInBytes(device)/1024 # KiB kibibyte (1024 bytes)
        disk_alignment = 4096 # Set alignment to 4MB [in KiB]
        partition_ranges = []
        if type == 0:
            partition_ranges.append("%s %s" %(disk_alignment,'-1s'))
        elif type == 1:
            psize = int(dsiz) / 2
            partition_ranges.append("%s %s" %(disk_alignment,psize))
            partition_ranges.append("%s %s" %(psize, '-1s'))
        elif type == 2:
            psize = int(dsiz) / 4
            partition_ranges.append("%s %s" %(disk_alignment,psize))
            partition_ranges.append("%s %s" %(psize, '-1s'))
        elif type == 3:
            psize = int(dsiz) / 10
            partition_ranges.append("%s %s" %(disk_alignment,psize))
            partition_ranges.append("%s %s" %(psize, '-1s'))
        elif type == 4:
            psize = int(dsiz) / 100 * 3
            partition_ranges.append("%s %s" %(disk_alignment,psize))
            partition_ranges.append("%s %s" %(psize, '-1s'))
        elif type == 5:
            psize = int(dsiz) / 100
            partition_ranges.append("%s %s" %(disk_alignment,psize))
            partition_ranges.append("%s %s" %(psize, '-1s'))
# if this fails disk probably kaput:
        ret = os.system("dd bs=1 seek=446 count=64 if=/dev/zero of=/dev/%s" % device)
        if ret != 0:
            return -3
        try:
            for p_range in partition_ranges:
                cmd = "parted -s /dev/%s -- unit KiB mkpart primary %s" % (device, p_range)
                print  "[PB Disks]  ---> execute: %s \n" % cmd 
                sfdisk1 = os.popen(cmd, "w")
            print "[PB Disks] Rescan partitions ..."
            os.system("partprobe /dev/%s" % device)
        except:
            return -2
        return 0

    # return value:
    # 0 -> ok
    # -1 -> umount failed
    # -2 -> sfdisk failed
    def chkfs(self, device, partition):
        fdevice = "%s%d" % (device, partition)
        print "[PB Disks] checking device %s" % fdevice
        if self.isMountedP(device, partition):
            oldmp = self.getMountedP(device, partition)
#            print "[PB Disks] partition is mounted... umount"
            if not self.umountP(device, partition):
#                print "[PB Disks] umount failed!"
                return -1
        else:
            oldmp = ""
        if self.isMountedP(device, partition):
                return -1

        ret = os.system("/sbin/fsck.ext3 -aV /dev/%s || /sbin/fsck.ext2 -aV /dev/%s || /usr/sbin/fsck.vfat -aV /dev/%s || /sbin/fsck.ext4 -aV /dev/%s " % (fdevice, fdevice, fdevice, fdevice))

        if len(oldmp) > 0:
            self.mount(fdevice, oldmp)

        if ret == 0:
            return 0
        return -2;

#####
    def mkfs2(self, device, partition):
        dev = "%s%d" % (device, partition)
        size = 0
        partitions = open("/proc/partitions")
        for part in partitions:
            res = re.sub("\s+", " ", part).strip().split(" ")
            if res and len(res) == 4:
                if res[3] == dev:
                    size = int(res[2])
                    break

        if size == 0:
            return -1

        if self.isMountedP(device, partition):
            oldmp = self.getMountedP(device, partition)
#            print "[PB Disks] partition is mounted... umount"
            if not self.umountP(device, partition):
#                print "[PB Disks] umount failed!"
                return -2
        else:
            oldmp = ""

        helper = "/dev/" + device
        helper2 = helper + str(partition)
        helper3 = "fdisk -l " + helper + " | grep " + helper2
        partids = os.popen(helper3)
        partid = partids.read().strip()
        partids.close()
        if "Linux" not in partid:
            cmd2 = "/usr/sbin/sfdisk "
            cmd2 += "-c /dev/" + device + " " + str(partition) + " 83"
            os.system(cmd2)

        cmd = "/sbin/mkfs.ext2 "
        if size > 4 * 1024 * 1024 * 1024:
            cmd += "-T largefile "
        cmd += " -v -m0 /dev/" + dev
        ret = os.system(cmd)

        if len(oldmp) > 0:
            self.mount(dev, oldmp)

        if ret == 0:
            return 0
        return -3;

    def mkfs3(self, device, partition):
        dev = "%s%d" % (device, partition)
        size = 0
        partitions = open("/proc/partitions")
        for part in partitions:
            res = re.sub("\s+", " ", part).strip().split(" ")
            if res and len(res) == 4:
                if res[3] == dev:
                    size = int(res[2])
                    break

        if size == 0:
            return -1

        if self.isMountedP(device, partition):
            oldmp = self.getMountedP(device, partition)
#            print "[PB Disks] partition is mounted... umount"
            if not self.umountP(device, partition):
#                print "[PB Disks] umount failed!"
                return -2
        else:
            oldmp = ""

        helper = "/dev/" + device
        helper2 = helper + str(partition)
        helper3 = "fdisk -l " + helper + " | grep " + helper2
        partids = os.popen(helper3)
        partid = partids.read().strip()
        partids.close()
        if "Linux" not in partid:
            cmd2 = "/usr/sbin/sfdisk "
            cmd2 += "-c /dev/" + device + " " + str(partition) + " 83"
            os.system(cmd2)

        cmd = "/sbin/mkfs.ext3 "
        if size > 4 * 1024 * 1024 * 1024:
            cmd += "-T largefile "
        cmd += "-m0 /dev/" + dev
        ret = os.system(cmd)

        if len(oldmp) > 0:
            self.mount(dev, oldmp)

        if ret == 0:
            return 0
        return -3;

    def mkfs4(self, device, partition):
        dev = "%s%d" % (device, partition)
        size = 0
        partitions = open("/proc/partitions")
        for part in partitions:
            res = re.sub("\s+", " ", part).strip().split(" ")
            if res and len(res) == 4:
                if res[3] == dev:
                    size = int(res[2])
                    break

        if size == 0:
            return -1

        if self.isMountedP(device, partition):
            oldmp = self.getMountedP(device, partition)
#            print "[PB Disks] partition is mounted... umount"
            if not self.umountP(device, partition):
#                print "[PB Disks] umount failed!"
                return -2
        else:
            oldmp = ""

        helper = "/dev/" + device
        helper2 = helper + str(partition)
        helper3 = "fdisk -l " + helper + " | grep " + helper2
        partids = os.popen(helper3)
        partid = partids.read().strip()
        partids.close()
        if "Linux" not in partid:
            cmd2 = "/usr/sbin/sfdisk "
            cmd2 += "-c /dev/" + device + " " + str(partition) + " 83"
            os.system(cmd2)

        cmd = "/sbin/mkfs.ext4 "
        if size > 250 * 1024 * 1024 * 1024:
            cmd += "-T largefile  -N 262144 sparse_super dir_index "
        elif size > 16 * 1024 * 1024 * 1024:
            cmd += "-T largefile sparse_super "
        elif size > 2 * 1024 * 1024 * 1024:
            cmd += "-T largefile -N %s " %(int(size / 1024 / 1024 * 32))

#### disable journaling for removables (not really right for USB mechanical HDD, check!!!)
        if self.isRemovable(device):
            cmd += " -O ^has_journal "
        cmd += " -v -m0 /dev/" + dev
        ret = os.system(cmd)

        if len(oldmp) > 0:
            self.mount(dev, oldmp)

        if ret == 0:
            return 0
        return -3;


    def mkfsvfat(self, device, partition):
        dev = "%s%d" % (device, partition)
        size = 0
        partitions = open("/proc/partitions")
        for part in partitions:
            res = re.sub("\s+", " ", part).strip().split(" ")
            if res and len(res) == 4:
                if res[3] == dev:
                    size = int(res[2])
                    break

        if size == 0:
            return -1

        if self.isMountedP(device, partition):
            oldmp = self.getMountedP(device, partition)
#            print "[PB Disks] partition is mounted... umount"
            if not self.umountP(device, partition):
#                print "[PB Disks] umount failed!"
                return -2
        else:
            oldmp = ""
        
        helper = "/dev/" + device
        helper2 = helper + str(partition)
        helper3 = "fdisk -l " + helper + " | grep " + helper2
        partids = os.popen(helper3)
        partid = partids.read().strip()
        partids.close()
        if "FAT32" not in partid:
            cmd2 = "/usr/sbin/sfdisk "
            cmd2 += "-c /dev/" + device + " " + str(partition) + " b"
            os.system(cmd2)

        cmd = "/usr/sbin/mkfs.vfat "
        cmd += " -F 32 /dev/" + dev
        ret = os.system(cmd)

        if len(oldmp) > 0:
            self.mount(dev, oldmp)

        if ret == 0:
            return 0
        return -3;

    def ausl(self, device, partition):
        mnt = self.getMountedP(device, partition)
#        print "[PB Disks] mnt ", mnt
        fshelp = os.popen("mount | grep %s" %mnt)
        fs = fshelp.read().strip()
        fshelp.close()
#        print "[PB Disks] fshelp ", fshelp
#        print "[PB Disks] fs ", fs
    
        if self.isMountedP(device, partition):
            if "ext" in fs:
                if os.access("%s/tanja" %mnt, os.F_OK):
                    print "[PB Disks] fshelp Loesche altes Verzeichnis, da moeglicherweise alte Sachen enthalten ist"
                    os.renames("%s/tanja" %mnt, "%s/delete" %mnt)
                    os.system("rm -rf %s/delete"%mnt)
                    print "[PB Disks]  Altes Verzeichnis geloescht"
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
                    print "[PB Disks] Verzeichnisse erstellt"
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
                    print "[PB Disks] Dateien kopiert"
                    r = subprocess.Popen("echo %s >> /etc/enigma2/.tanja" %mnt, shell=True)
                    r.wait
                    print "[PB Disks] Kontroll-/Pfaddatei angelegt"
                    time.sleep(60)
                    print "[PB Disks] Kontroll-/Pfaddatei angelegt"
                    return 0
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
                    print "[PB Disks] Verzeichnisse erstellt"
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
                    print "[PB Disks] Dateien kopiert"
                    r = subprocess.Popen("echo %s >> /etc/enigma2/.tanja" %mnt, shell=True)
                    r.wait
                    print "[PB Disks] Kontroll-/Pfaddatei angelegt"
                    time.sleep(60)
                    print "[PB Disks] Kontroll-/Pfaddatei angelegt"
                    return 0
            else:
                return 2
        else:
            return 1


    def raus(self, device, partition):
        if os.access("/etc/enigma2/.tanja", os.F_OK):
            print "[PB Disks] Es ist ausgelagert..."
            os.system("mv /etc/enigma2/.tanja /etc/enigma2/.tanjaremove")
            print "[PB Disks] Kontrolldatei umbenannt um beim Neustarten das Verzeichnis zu loeschen"
            return 0
        else:
            return 1

#### MountPoints 
class MountPoints():
    def __init__(self):
        self.entries = []
        boxinfo = BoxInfo()
        boxinfo.detectBox()
        self.settingsMounts = boxinfo.settingsMounts

    def read(self):
        self.entries = []
        conf = open(self.settingsMounts, "r")
        for line in conf:
            res = line.strip().split(":")
            if res and len(res) == 4:
                self.entries.append(res)
        conf.close()

    def write(self):
        conf = open(self.settingsMounts, "w")
        for entry in self.entries:
            conf.write("%s:%s:%s:%s\n" % (entry[0], entry[1], entry[2], entry[3]))
        conf.close()

    def checkPath(self, path):
        for entry in self.entries:
            if entry[0] == path:
                return True
        return False

    def isMounted(self, path):
        mounts = open("/proc/mounts")
        for mount in mounts:
            res = mount.split(" ")
            if res and len(res) > 1:
                if res[1] == path:
                    mounts.close()
                    return True
        mounts.close()
        return False

    def umount(self, path):
        return os.system("umount %s" % path) == 0

    def mount(self, device, partition, path):
        return os.system("[ ! -d %s ] && mkdir %s\nmount /dev/%s%s %s" % (path, path, device, partition, path)) == 0

    def exist(self, path):
        for entry in self.entries:
            if entry[0] == path:
                return True
        return False

    def delete(self, path):
        for entry in self.entries:
            if entry[0] == path:
                self.entries.remove(entry)
#####
        harddiskmanager.removeMountedPartition(path + '/')
#####

    def deleteDisk(self, device):
        for i in range(1,4):
            res = self.get(device, i)
            if len(res) > 0:
                self.delete(res)

    def add(self, device, partition, path):
        if os.access("/sys/block/%s/device/vendor" % device, os.F_OK):
            vendor = open("/sys/block/%s/device/vendor" % device, "r").read().strip()
        else:
            vendor = "IDE"
        if os.access("/sys/block/%s/device/model" % device, os.F_OK):
            model = open("/sys/block/%s/device/model" % device, "r").read().strip()
        elif os.access("/proc/ide/%s/model" % device, os.F_OK):
            model = open("/proc/ide/%s/model" % device, "r").read().strip()
        else:
            model = "unknown or nothing"
        for entry in self.entries:
            if entry[1] == model and entry[2] == vendor and entry[3] == partition:
                entry[0] = path
                return
        self.entries.append([ path, model, vendor, str(partition) ])
#####
        harddiskmanager.addMountedPartition(path + '/', model)
#####

##### e.g. /sys/block/sda/device/model='SD/MMC' or 'USB SD Reader' /sys/block/sda/device/vendor=Generic-
    def get(self, device, partition): 
        if os.access("/sys/block/%s/device/vendor" % device, os.F_OK):
            vendor = open("/sys/block/%s/device/vendor" % device, "r").read().strip()
        else:
            vendor = "IDE"
        if os.access("/sys/block/%s/device/model" % device, os.F_OK):
            model = open("/sys/block/%s/device/model" % device, "r").read().strip()
        elif os.access("/proc/ide/%s/model" % device, os.F_OK):
            model = open("/proc/ide/%s/model" % device, "r").read().strip()
        else:
            model = "unknown or nothing"
        for entry in self.entries:
            print "[PB Mountpoints entry] ", entry
            if entry[1] == model and entry[2] == vendor and entry[3] == partition:
                return entry[0]

        return ""


#######################################
## HELPER FUNCTIONS 
#######################################
class ExtraActionBox(Screen):
    def __init__(self, session, message, title, action):
        Screen.__init__(self, session)
        self.session = session
        self.ctitle = title
        self.caction = action
        self.skin = """
            <screen name="ExtraActionBox" position="center,center" size="560,70" title=" ">
                <widget alphatest="on" name="logo" position="10,10" size="48,48" transparent="1" zPosition="2" />
                <widget font="Regular;20" halign="center" name="message" position="60,10" size="490,48" valign="center" />
            </screen>"""

        self["message"] = Label(message)
        self["logo"] = Pixmap()
        self.timer = eTimer()
        self.timer.callback.append(self.__setTitle)
        self.timer.start(200, 1)

    def __setTitle(self):
        if self["logo"].instance is not None:
            self["logo"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/run.png")
        self.setTitle(self.ctitle)
        self.timer = eTimer()
        self.timer.callback.append(self.__start)
        self.timer.start(200, 1)

    def __start(self):
        self.close(self.caction())


class DialogFormat(Screen):

    skin = """
        <screen name="DialogFormat" position="60,245" size="600,10" title="PB Format Utility">
        <widget name="text" position="65,8" size="520,0" font="Regular;22" />
        <widget name="QuestionPixmap" pixmap="skin_default/icons/input_question.png" position="5,5" size="53,53" alphatest="on" />
        <widget name="list" position="100,100" size="480,525" />
        <applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth = self.instance.size().width()
orgpos = self.instance.position()
textsize = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 50)
offset = 0
offset = 100
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
#### needs checking 2.6.18 has no ext4, some newer do not have ext3, actually only for Ferrariclones
####        self.list = [ (_("Format ext2"), 0), (_("Format ext3"), 1), (_("Format fat32"), 2), (_("Format ext4"), 3) ]
        self.list = [ (_("Format ext2"), 0), (_("Format ext3"), 1), (_("Format fat32"), 2) ]
        if isFileSystemSupported("ext4"):
            self.list.append((_("Format ext4"), 3))
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

#### SimpleEntry
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
        res.append(MultiContentEntryText(pos=(60, 5), size=(1000, 38), font=0, text=name))
    else:
    # Estuary - End Here
        res.append(MultiContentEntryText(pos=(60, 10), size=(420, 38), font=0, text=name))

    return res

#### ExtrasList
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
            self.l.setFont(0, gFont('Regular', 20))
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

def MessageBoxEntry(name, picture):
    res = [(name, picture)]
    #res = []
    picture = ('/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/' + picture)

    if fileExists(picture):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(48, 48), png=loadPNG(picture)))
    res.append(MultiContentEntryText(pos=(65, 10), size=(425, 38), font=0, text=name))

    return res

class ExtraMessageBox(Screen):
    def __init__(self, session, message = "", title = "", menulist = [], type = 0, exitid = -1, default = 0, timeout = 0):
        # type exist for compability... will be ignored
        Screen.__init__(self, session)
        self.session = session
        self.ctitle = title
        self.exitid = exitid
        self.default = default
        self.timeout = timeout
        self.elapsed = 0
        self.list = []
        for item in menulist:
            self.list.append(MessageBoxEntry(item[0], item[1]))

        self['menu'] = ExtrasList(self.list)
        self["menu"].onSelectionChanged.append(self.selectionChanged)

        self["message"] = Label(message)
        self["actions"] = ActionMap(["SetupActions"],
        {
            "ok": self.ok,
            "cancel": self.cancel
        }, -2)

        self.onLayoutFinish.append(self.layoutFinished)

        self.timer = eTimer()
        self.timer.callback.append(self.timeoutStep)
        if self.timeout > 0:
            self.timer.start(1000, 1)

    def selectionChanged(self):
        self.timer.stop()
        self.setTitle(self.ctitle)

    def timeoutStep(self):
        self.elapsed += 1
        if self.elapsed == self.timeout:
            self.ok()
        else:
            self.setTitle("%s - %d" % (self.ctitle, self.timeout - self.elapsed))
            self.timer.start(1000, 1)

    def layoutFinished(self):
        if self.timeout > 0:
            self.setTitle("%s - %d" % (self.ctitle, self.timeout))
        else:
            self.setTitle(self.ctitle)
        self['menu'].moveToIndex(self.default)

    def ok(self):
        index = self['menu'].getSelectedIndex()
        self.close(index)

    def cancel(self):
        if self.exitid > -1:
            self.close(self.exitid)


### TODO: worked only for DMM ? recheck !!!
class BoxInfo():
    def __init__(self):
        self.isIPBOX = False
        self.isDMM = False
        self.scriptsPath = ""
        self.settingsMounts = ""
        self.settingsModules = ""
        self.settingshdparm = ""
        self.sfdiskBin = ""

    def detectBox(self):
        self.scriptsPath = "/usr/script/"
        self.settingsMounts = "/etc/enigma2/settings.mounts"
        self.settingsModules = "/etc/enigma2/settings.modules"
        self.settingshdparm = "/etc/enigma2/settings.hdparm"
        self.sfdiskBin = "/usr/sbin/sfdisk"

