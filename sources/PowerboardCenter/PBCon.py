#'''
#Created on 2013-07-15
#
#@author: stibbich <stibbich@pb-powerboard.com>
#'''
##########################################################
# -*- coding: utf-8 -*-

from enigma import eConsoleAppContainer
from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel

class PBConsole2(Screen):
    skin = """
    <screen position="100,100" size="1000,600" title="busybox command execution..." >
        <widget name="text" position="0,0" size="800,580" font="Console;14" />
    </screen>"""

    def __init__(self, session, title = "PB-Powerboard", cmdlist = None, finishedCallback = None, closeOnSuccess = False):
        Screen.__init__(self, session)

        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.errorOcurred = False

        self["text"] = ScrollLabel("")
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
        {
            "ok": self.cancel,
            "back": self.cancel,
            "up": self["text"].pageUp,
            "down": self["text"].pageDown
        }, -1)

        self.cmdlist = cmdlist
        self.newtitle = title

        self.onShown.append(self.updateTitle)

        self.container = eConsoleAppContainer()
        self.run = 0
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.dataAvail)
        self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self["text"].setText(_("Execution progress:") + "\n\n")
        print "Console: executing in run", self.run, " the command:", self.cmdlist[self.run]
        if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
            self.runFinished(-1) # so we must call runFinished manual

    def runFinished(self, retval):
        if retval:
            self.errorOcurred = True
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
                self.runFinished(-1) # so we must call runFinished manual
        else:
            lastpage = self["text"].isAtLastPage()
            str = self["text"].getText()
            str += _("Execution finished!!");
            self["text"].setText(str)
            if lastpage:
                self["text"].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not self.errorOcurred and self.closeOnSuccess:
                self.cancel()

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)

    def dataAvail(self, str):
        lastpage = self["text"].isAtLastPage()
        self["text"].setText(self["text"].getText() + str)
        if lastpage:
            self["text"].lastPage()

