#!/bin/sh
#DESCRIPTION=Erstellt ein Backup der cams und configs!
echo "*******************************************"
echo "*      .--.                               *"
echo "*     |o_o |                              *"
echo "*     |\_/ | POWERBOARD-TEAM 2010 / 2011  *"
echo "*    //    \\                              *"
echo "*   (|     | )                            *"
echo "*  / \_   _/ \                            *"
echo "*  \___)-(___/                            *"
echo "*******************************************"
	sleep 1
echo "Sichere cams und configs!"

echo "Backuppfad auslesen"
backupentry=`cat /etc/enigma2/settings | grep "config.misc.backup_path"`
backuppath=${backupentry:24}

if [ -z $backupentry ]; then
	echo "Kein Backuppfad angegeben!"
	echo "Backup wird beendet"
	sleep 5
	exit 0
else
	backuppathcomp=$backuppath"backup"
	echo $backuppath
	echo ""
	echo "Backup wird nach "$backuppathcomp
	echo "geschrieben"
	echo ""
	if [ ! -e $backuppathcomp ]; then
		mkdir $backuppathcomp
	fi
	wait
	if [ -e $backuppathcomp ]; then
		echo "Erstellt Backup-tarball..."
		mkdir /tmp/backuptmp
		mkdir /tmp/backuptmp/usr
		mkdir /tmp/backuptmp/usr/bin
		mkdir /tmp/backuptmp/usr/script
		mkdir /tmp/backuptmp/usr/keys
		mkdir /tmp/backuptmp/usr/scam
		mkdir /tmp/backuptmp/etc
		mkdir /tmp/backuptmp/etc/tuxbox
#		mkdir /tmp/backuptmp/etc/tuxbox/config
		cp -rf /usr/bin/cam /tmp/backuptmp/usr/bin/
		cp -rf /usr/script/cam /tmp/backuptmp/usr/script/
		cp /etc/clist.list /tmp/backuptmp/etc/clist.list
		cp -rf /etc/tuxbox/conf*  /tmp/backuptmp/etc/tuxbox/
# camd3 config
		[ -e /usr/keys/camd3.config ] && cp /usr/keys/camd3.config /tmp/backuptmp/usr/keys/camd3.config
		[ -e /usr/keys/camd3.users ] && cp /usr/keys/camd3.users /tmp/backuptmp/usr/keys/camd3.users
		[ -e /usr/keys/camd3.servers ] && cp /usr/keys/camd3.servers /tmp/backuptmp/usr/keys/camd3.servers
# mgcamd config
		[ -e /usr/keys/mg_cfg ] && cp /usr/keys/mg_cfg /tmp/backuptmp/usr/keys/mg_cfg
		[ -e /usr/keys/ignore.list ] && cp /usr/keys/ignore.list /tmp/backuptmp/usr/keys/ignore.list
		[ -e /usr/keys/priority.list ] && cp /usr/keys/priority.list /tmp/backuptmp/usr/keys/priority.list
		[ -e /usr/keys/replace.list ] && cp /usr/keys/replace.list /tmp/backuptmp/usr/keys/replace.list
		[ -e /etc/radegast.cfg ] && cp /etc/radegast.cfg /tmp/backuptmp/etc/radegast.cfg
		[ -e /etc/tuxbox/config/newcamd.conf ] && cp /etc/tuxbox/config/newcamd.conf /tmp/backuptmp/etc/tuxbox/config/newcamd.conf
# scam config
		[ -e /usr/scam/ca_servers ] && cp /usr/scam/ca_servers /tmp/backuptmp/usr/scam/ca_servers
		[ -e /usr/scam/cw_feeds ] && cp /usr/scam/cw_feeds /tmp/backuptmp/usr/scam/cw_feeds
		[ -e /usr/scam/cw_servers ] && cp /usr/scam/cw_servers /tmp/backuptmp/usr/scam/cw_servers
		[ -e /usr/scam/local_ca_server ] && cp /usr/scam/local_ca_server /tmp/backuptmp/usr/scam/local_ca_server
# gbox config
		[ -e /usr/keys/gbox_cfg ] && cp /usr/keys/gbox_cfg /tmp/backuptmp/usr/keys/gbox_cfg
		[ -e /usr/keys/softcam.cfg ] && cp /usr/keys/softcam.cfg /tmp/backuptmp/usr/keys/softcam.cfg
		[ -e /usr/keys/cwshare.cfg ] && cp /usr/keys/cwshare.cfg /tmp/backuptmp/usr/keys/cwshare.cfg
# cccam config
		[ -e /etc/CCcam.cfg ] && cp /etc/CCcam.cfg /tmp/backuptmp/etc/CCcam.cfg
		[ -e /etc/CCcam.channelinfo ] && cp /etc/CCcam.channelinfo /tmp/backuptmp/etc/CCcam.channelinfo
		[ -e /etc/CCcam.prio ] && cp /etc/CCcam.prio /tmp/backuptmp/etc/CCcam.prio
		[ -e /etc/CCcam.providers  ] && cp /etc/CCcam.providers  /tmp/backuptmp/etc/CCcam.providers
		
#na hoffentlich sind das alle der konfigurierdichzutodecam ;)
		backup=$backuppathcomp"/camsandconfigs.tar.gz *"
		cd /tmp/backuptmp
		tar -czf $backup
		wait
		chmod 666 $backup
		rm -rf /tmp/backuptmp
		wait
		echo "Backup-tarball erstellt."
	else
		echo "Kann kein Backup anlegen."
	fi
	echo ""
fi
exit 0
