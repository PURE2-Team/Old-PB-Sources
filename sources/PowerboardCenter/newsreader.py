# -*- coding: utf-8 -*-
from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label
from Components.GUIComponent import *
from Components.MenuList import MenuList
from Components.Input import Input
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
import os,sys
from Plugins.Plugin import PluginDescriptor
###
import ConfigParser
from pyexpat import *
import sys,urllib,re
from re import sub
        
sys.path.append("/usr/lib/python2.6/xml/sax/")
import xml.dom.minidom 
###############################################################################        
myname = "Newsreader"     
myversion = "1.1"
###############################################################################        
def main(session,**kwargs):
    session.open(FeedScreenList)

def autostart(reason,**kwargs):
    pass
        
###############################################################################        
###############################################################################        
class FeedScreenList(Screen):
    skin = """
        <screen position="center,center" size="600,400" title="%s" >
            <widget name="menu" position="0,0" size="400,400" scrollbarMode="showOnDemand" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/pb_small.png" position="440,250" size="150,150" backgroundColor="black" alphatest="blend" />
        </screen>""" % myname
        
    def __init__(self, session, args = 0):
        self.skin = FeedScreenList.skin
        self.session = session
        Screen.__init__(self, session)
        self.menu = args
         
            
        self["menu"] = MenuList(self.getFeedList())
        self["actions"] = ActionMap(["WizardActions", "DirectionActions","MenuActions"], 
            {
             "ok": self.go,
             "back": self.close,
             "menu": self.openMainMenu,
             }, -1)
        self.onShown.append(self.updateValues)
        
    def updateValues(self):
        self["menu"].l.setList(self.getFeedList())       
                
    def go(self):
        cmd = self["menu"].l.getCurrentSelection()[1]
        if cmd is "about":
            self.session.open(MessageBox,_("%s Enigma2 Plugin V%s\n\n%s written by stibbich\n\nhttp://www.pb-powerboard.com\n\nbased on code from 3c5x9" % (myname,myversion,myname)), MessageBox.TYPE_INFO)
        elif cmd.startswith("showfeed_"):
            feedname = cmd.split("_",1)[1]
            if self.config.isFeed(feedname):
                feed = self.config.getFeedByName(feedname)
                self.showFeed(feed)
            else:
                print "["+myname+"] section in config not found"

    def showFeed(self,feed):
        try:
            self.session.open(FeedScreenContent,feed)
        except IOError,e:
            pass
            #self.session.open(MessageBox,_("loading feeddata faild!\n\n%s" %e), MessageBox.TYPE_WARNING)
            
        except:
            self.session.open(MessageBox,_("While showing feed %s some error occurs" % feed.getName()), MessageBox.TYPE_INFO)            
    def openMainMenu(self):
        self.session.open(FeedreaderMenuMain,self.config)
    def getFeedList(self):
        self.config = FeedreaderConfig()    
        list = []
        for feed in self.config.getFeeds():
            list.append((_(feed.getName()), "showfeed_%s" % feed.getName()))
        list.sort()
        return list
############################################################################### 
class FeedreaderConfig:
    configfile = "/etc/enigma2/rssreader.conf"
    def __init__(self):
        self.configparser = ConfigParser.ConfigParser()
        self.configparser.read(self.configfile)
    def getFeeds(self):
        feeds=[]
        sections = self.configparser.sections()
        for section in sections:
            if section.startswith("FEED") is True:
                feed = self.getFeedByName(section[4:])
                feeds.append(feed)
        return feeds
    def isFeed(self,feedname):
        if self.configparser.has_section("FEED%s"%feedname) is True:
            return True
        else:
            return False
    def getFeedByName(self,feedname):
        if self.isFeed(feedname) is True:
            feed = Feed(
                        feedname,
                        self.configparser.get("FEED%s"%feedname, "description"),
                        self.configparser.get("FEED%s"%feedname, "url"),
                    )
            feed.setFavorite()
            return feed
        else:
            return False
    def getProxysettings(self):
        if self.configparser.has_section("PROXY") is True:
            proxysettings = {}
            if self.configparser.has_option("PROXY", "HTTP") is True:
                proxysettings['http'] = self.configparser.get("PROXY", "HTTP")
            if self.configparser.has_option("PROXY", "FTP") is True:
                proxysettings['ftp'] = self.configparser.get("PROXY", "FTP")
            if self.configparser.has_option("PROXY", "useproxy") is True:
                if self.configparser.get("PROXY", "useproxy").startswith("true") is True:
                    return proxysettings
                else:
                    return None
            else:
                return None
        else:
            return None
    def addFeed(self,feed):
        try:
            self.configparser.add_section("FEED%s"%feed.getName())
            #self.configparser.set("FEED%s"%feed.getName(), "name", feed.getName())
            self.configparser.set("FEED%s"%feed.getName(), "description", feed.getDescription())
            self.configparser.set("FEED%s"%feed.getName(), "url", feed.getURL())
            self.writeConfig()
            return True,"Feed added"
        except ConfigParser.DuplicateSectionError:
            return False,"Feed exists already!"

    def changeFeed(self,feedold,feednew):
        if self.configparser.has_section("FEED%s" %feedold.getName()) is False:
            print "OLD: '%s'" %feedold.getName()
            print "NEW: '%s'" %feednew.getName()
            return False,"feed not found in config"
        elif self.configparser.has_section("FEED%s" %feednew.getName()) is True:
            return False,"feed with that name exists already"
        else:    
           self.configparser.remove_section("FEED%s" %feedold.getName())
           return self.addFeed(feednew); 
        
    def deleteFeedWithName(self,feedname):
        self.configparser.remove_section("FEED%s" %feedname)
        self.writeConfig()
        
    def writeConfig(self):
        fp = open(self.configfile,"w")
        self.configparser.write(fp)
        fp.close()

############################################################################### 
class Feed:
    isfavorite = False
    def __init__(self,name,description,url):
        self.name = name
        self.description = description
        self.url = url
    def getName(self):
        return self.name
    def getDescription(self):
        return self.description
    def getURL(self):
        return self.url
    def setName(self,name):
        self.name = name
    def setDescription(self,description):
        self.description = description
    def setURL(self,url):
        self.url = url
    def setFavorite(self):
        self.isfavorite = True
    def isFavorite(self):
        return self.isfavorite
    
    
############################################################################### 
class FeedreaderMenuMain(Screen):
    def __init__(self, session, config = 0):
        self.config = FeedreaderConfig()
        self.skin = """
                <screen position="center,center" size="500,400" title="Main Menu" >
                    <widget name="menu" position="10,10" size="500,400" scrollbarMode="showOnDemand" />
                </screen>""" 
        self.session = session
        Screen.__init__(self, session)
        list = []
        list.append((_("change Feed"), "feed_change"))
        list.append((_("add new Feed"), "feed_add"))
        list.append((_("delete Feed from favorites"), "feed_delete"))
        list.append((_("about %s" % myname), "about"))
                    
        self["menu"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
                                        {
                                         "ok": self.go,
                                         "back": self.close,
                                         }
                                        , -1)
    def go(self):
        selection = self["menu"].l.getCurrentSelection()
        if selection is not None:
            cmd = selection[1]
            if cmd is "about":
                self.session.open(MessageBox,_("%s Enigma2 Plugin V%s\n\nhttp://pb-powerboard.com" % (myname,myversion)), MessageBox.TYPE_INFO)
            elif cmd is "feed_delete":
                WizzardDeleteFeed(self.session)
            elif cmd is "feed_add":
                WizzardAddFeed(self.session)
            elif cmd is "feed_change":
                self.showFeedsToChange()

    def showFeedsToChange(self):
        self.config = FeedreaderConfig()
        feeds = self.config.getFeeds()
        feedlist = []
        for feed in feeds:
            feedlist.append((_(feed.getName()),feed.getName()))
        self.session.openWithCallback(self.feed2changeSelected,ChoiceBox,_("select Feed to change"),feedlist)
    def feed2changeSelected(self,selected):
        try:
            feed = self.config.getFeedByName(selected[1]);
            WizzardAddFeed(self.session,[feed.getName(),feed.getDescription(),feed.getURL(),True])
        except: 
            pass
###############################################################################        
class WizzardAddFeed(Screen):
    name = ""
    description = ""
    url = "http://"
    changefeed = False
    def __init__(self, session,args=0):
        if args is not 0:
            self.name = args[0].rstrip()
            self.description = args[1]
            self.url = args[2]
            self.changefeed = args[3]
            self.feedold= Feed(self.name,self.description,self.url)
        self.session = session
        self.session.openWithCallback(self.name_entered,InputBox, title=_("Please enter a name for the new Feed"), text=self.name, maxSize=False, type=Input.TEXT)
    def name_entered(self,feedname):
        if feedname is None:
            self.cancelWizzard()
        else:
            self.name = feedname
            self.session.openWithCallback(self.url_entered,InputBox, title=_("Please enter a url for the new Feed"), text=self.url, maxSize=False, type=Input.TEXT)
    def url_entered(self,feedurl):
        if feedurl is None:
            self.cancelWizzard()
        else:
            self.url = feedurl
            self.session.openWithCallback(self.description_entered,InputBox, title=_("Please enter a description for the new Feed"), text=self.description, maxSize=False, type=Input.TEXT)
    def description_entered(self,feeddescription):
        if feeddescription is None:
            self.cancelWizzard()
        else:
            self.description = feeddescription
            feednew = Feed(self.name.rstrip(),self.description,self.url)
            config = FeedreaderConfig()
            if self.changefeed is True:
                result,text = config.changeFeed(self.feedold,feednew)
                if result is True:
                    self.session.open(MessageBox,_(text), MessageBox.TYPE_INFO)
                else:
                    self.session.open(MessageBox,_("changing feed faild!\n\n%s" %text), MessageBox.TYPE_WARNING)
                 
            else:
                result,text = config.addFeed(feednew)
                if result is True:
                    self.session.open(MessageBox,_(text), MessageBox.TYPE_INFO)
                else:
                    self.session.open(MessageBox,_("adding feed faild!\n\n%s" %text), MessageBox.TYPE_WARNING)
                
    def cancelWizzard(self):
        #self.session.open(MessageBox,_("adding was canceled"), MessageBox.TYPE_WARNING)
        pass
###############################################################################        
class WizzardDeleteFeed(Screen):
    def __init__(self, session):
        self.session = session
        self.config = FeedreaderConfig()
        feeds = self.config.getFeeds()
        feedlist = []
        for feed in feeds:
            feedlist.append((_(feed.getName()),feed.getName()))
        self.session.openWithCallback(self.feed2deleteSelected,ChoiceBox,_("select Feed to delete"),feedlist)
        
    def feed2deleteSelected(self,selectedfeedname):
        if selectedfeedname is None:
            self.cancelWizzard()
        else:
            self.feed2delete = selectedfeedname[1]
            self.session.openWithCallback(self.userIsSure,MessageBox,_("are you sure to delete this Feed?\n\n%s" % self.feed2delete), MessageBox.TYPE_YESNO)

    def userIsSure(self,answer):
        if answer is None:
            self.cancelWizzard()
        if answer is False:
            self.cancelWizzard()
        else:
            self.config.deleteFeedWithName(self.feed2delete)
            
    def cancelWizzard(self):
        pass
###############################################################################        
        
class FeedScreenContent(Screen):
    def __init__(self, session, args = 0):
        self.feed = args
        self.skin = """
                <screen position="center,center" size="650,400" title="%s" >
                    <widget name="menu" position="10,10" size="650,400" scrollbarMode="showOnDemand" />
                </screen>""" % (self.feed.getName())
        self.session = session
        Screen.__init__(self, session)
        
        list = []
        self.itemlist=[]    
        itemnr=0
        for item in self.getFeedContent(self.feed):
            list.append((_(item["title"]), itemnr))
            self.itemlist.append(item)
            itemnr = itemnr+1
        self.menu = args
                
        self["menu"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions", "DirectionActions","MenuActions"], 
                                        {
                                         "ok": self.go,
                                         "back": self.close,
                                         "menu": self.openmenu,
                                         }
                                        , -1)
    def getFeedContent(self,feed):
        print "["+myname+"] reading feedurl '%s' ..." % (feed.getURL())
        try:
            self.rss = RSS()
            self.feedc = self.rss.getList(feed.getURL())
            print "["+myname+"] have got %i items in newsfeed " % len(self.feedc)
            return self.feedc
        except IOError:
            print "["+myname+"] IOError by loading the feed! Feedadress correct?"
            return []
        except:
            self.session.open(MessageBox,_("loading feeddata failed!" ), MessageBox.TYPE_WARNING)
            
            return []

    def go(self):
        selection = self["menu"].l.getCurrentSelection()
        if selection is not None:
            cmd = selection[1]
            item = self.itemlist[cmd]
            if item["type"].startswith("folder") is True:
                newitem = Feed(item["title"],item["desc"],item["link"])
                self.session.open(FeedScreenContent,newitem)

            elif item["type"].startswith("pubfeed") is True:
                newitem = Feed(item["title"],item["desc"],item["link"])
                self.session.open(FeedScreenContent,newitem)
            else:
                try:
                    self.session.open(FeedScreenItemviewer,[self.feed,item])
                except AssertionError:
                    self.session.open(MessageBox, _("Error while reading the feed"), MessageBox.TYPE_ERROR)

    def openmenu(self):
        if self.feed.isFavorite() is False:
            WizzardAddFeed(self.session,[self.feed.getName(),self.feed.getDescription(),self.feed.getURL(),False])
###############################################################################        
class FeedScreenItemviewer(Screen):
    skin = ""
    def __init__(self, session, args = 0):
        self.feed = args[0]
        self.item = args[1]
        xtitle = self.item['title'].replace('"','\'')
        self.skin = """
                <screen position="center,center" size="650,400" title="%s" >
                    <widget name="text" position="0,0" size="650,400" font="Regular;25" />
                </screen>""" % self.feed.getName()
        Screen.__init__(self, session)
        
        self["text"] = ScrollLabel(_(self.item['title']+"\n\n"+ self.item['desc']+"\n\n"+ self.item['date']+"\n"+self.item['link']))
        self["actions"] = ActionMap(["WizardActions"], 
                                    {
                                     "ok": self.close,
                                     "back": self.close,
                                     "up": self["text"].pageUp,
                                     "down": self["text"].pageDown
                                     }, -1)
#############################################################################
class RSS:
    DEFAULT_NAMESPACES = (
        None, # RSS 0.91, 0.92, 0.93, 0.94, 2.0
        'http://purl.org/rss/1.0/', # RSS 1.0
        'http://my.netscape.com/rdf/simple/0.9/' # RSS 0.90
    )
    DUBLIN_CORE = ('http://purl.org/dc/elements/1.1/',)

    def getElementsByTagName( self, node, tagName, possibleNamespaces=DEFAULT_NAMESPACES ):
        for namespace in possibleNamespaces:
            children = node.getElementsByTagNameNS(namespace, tagName)
            if len(children): return children
        return []

    def node_data( self, node, tagName, possibleNamespaces=DEFAULT_NAMESPACES):
        children = self.getElementsByTagName(node, tagName, possibleNamespaces)
        node = len(children) and children[0] or None
        return node and "".join([child.data.encode("utf-8") for child in node.childNodes]) or None

    def get_txt( self, node, tagName, default_txt="" ):
        """
        Liefert den Inhalt >tagName< des >node< zurueck, ist dieser nicht
        vorhanden, wird >default_txt< zurueck gegeben.
        """
        return self.node_data( node, tagName ) or self.node_data( node, tagName, self.DUBLIN_CORE ) or default_txt

    def print_txt( self, node, tagName, print_string ):
        """
        Formatierte Ausgabe
        """
        item_data = self.get_txt( node, tagName )
        if item_data == "":
            return
        print print_string % {
            "tag"   : tagName,
            "data"  : item_data
        }

    def print_rss( self, url ):
        rssDocument = xml.dom.minidom.parse( urllib.urlopen( url ,proxies=FeedreaderConfig().getProxysettings()) )

        for node in self.getElementsByTagName(rssDocument, 'item'):
            print '<ul class="RSS">'

            print '<li><h1><a href="%s">' % self.get_txt( node, "link", "#" )
            print self.get_txt( node, "title", "<no title>" )
            print "</a></h1></li>"

            self.print_txt( node, "date",           '<li><small>%(data)s</li>' )
            self.print_txt( node, "description",    '<li>%(data)s</li>' )
            print "</ul>"
    def getList( self, url ):
        """
        returns the content of the given URL as array
        """
        rssDocument = xml.dom.minidom.parse( urllib.urlopen( url,proxies=FeedreaderConfig().getProxysettings()) )
        channelname = self.get_txt( rssDocument, "title", "no channelname" )
        data =[]
        for node in self.getElementsByTagName(rssDocument, 'item'):
            nodex={}
            nodex['channel'] =  channelname
            nodex['type'] =  self.get_txt( node, "type", "feed" )
            nodex['link'] =  self.get_txt( node, "link", "" )
            nodex['title'] = self.convertHTMLTags(self.get_txt( node, "title", "<no title>" ))
            nodex['date'] =  self.get_txt( node, "pubDate", self.get_txt( node, "date", "" ) )
            nodex['desc'] =  self.convertHTMLTags(self.get_txt( node, "description", "" ))
            data.append(nodex)
        return data
    def convertHTMLTags(self,text_with_html):
        """
        removes all undisplayable things from text
        """
        charlist = []
        charlist.append(("&#228;","ä"))
        charlist.append(("&auml;","ä"))
        charlist.append(("&#252;","ü"))
        charlist.append(("&uuml;","ü"))
        charlist.append(("&#246;","ö"))
        charlist.append(("&ouml;","ö"))
        charlist.append(("&#196;","Ä"))
        charlist.append(("&Auml;","Ä"))
        charlist.append(("&#220;","Ü"))
        charlist.append(("&Uuml;","Ü"))
        charlist.append(("&#214;","Ö"))
        charlist.append(("&Ouml;","Ö"))
        charlist.append(("&#223;","ß"))
        charlist.append(("&szlig;","ß"))
        charlist.append(("&#038;","&"))
        charlist.append(("&#8230;","..."))
        charlist.append(("&#8211;","-"))
        charlist.append(("&#160;"," "))
        
        charlist.append(("&lt;","<"))
        charlist.append(("&gt;",">"))
        charlist.append(("&nbsp;"," "))
        charlist.append(("&amp;","&"))
        charlist.append(("&quot;","\""))
        
        
        # replace the define list
        for repl in charlist:
            text_with_html= text_with_html.replace(repl[0],repl[1])
        
        # delete all <*> Tags
        text_with_html = re.sub(r'<(.*?)>(?uism)', '', text_with_html)
        return text_with_html