#!/bin/sh
#DESCRIPTION=Erstellt ein Backup der Settings und Timer auf CF!
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
echo "Sichere Settings!"

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
		mkdir /tmp/backuptmp/etc
		mkdir /tmp/backuptmp/etc/tuxbox
		mkdir /tmp/backuptmp/usr
		mkdir /tmp/backuptmp/usr/share
		mkdir /tmp/backuptmp/usr/share/enigma2
		[ -e /etc/MultiQuickButton ] && cp -R /etc/MultiQuickButton /tmp/backuptmp/etc/MultiQuickButton
		[ -e /etc/samba ] && cp -R /etc/samba /tmp/backuptmp/etc
		[ -e /etc/exports ] && cp /etc/exports /tmp/backuptmp/etc/exports
		cp -R /etc/enigma2 /tmp/backuptmp/etc
		cp -R /etc/network /tmp/backuptmp/etc
		cp /etc/tuxbox/satellites.xml /tmp/backuptmp/etc/tuxbox/satellites.xml
		[ -e /etc/tuxbox/terrestrial.xml ] && cp /etc/tuxbox/terrestrial.xml /tmp/backuptmp/etc/tuxbox/terrestrial.xml
		[ -e /etc/tuxbox/cables.xml ] && cp /etc/tuxbox/cables.xml /tmp/backuptmp/etc/tuxbox/cables.xml
		cp /usr/share/enigma2/keymap.xml /tmp/backuptmp/usr/share/enigma2/keymap.xml
		wait
		backup=$backuppathcomp"/settings.tar.gz etc"
		cd /tmp/backuptmp
		tar -cpzf $backup
		wait
		chmod 666 $backuppathcomp"/settings.tar.gz"
		rm -rf /tmp/backuptmp
		wait
		echo "Backup-tarball erstellt."
	else
		echo "Kann kein Backup anlegen."
	fi
	echo ""
fi
exit 0
