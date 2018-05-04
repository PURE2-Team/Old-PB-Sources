#!/bin/sh
#DESCRIPTION=Stellt das Cams- und Configs-Backup wieder her!
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
echo "Spiele Cams und Configs Backup ein!"
echo "Backuppfad auslesen"
backupentry=`cat /etc/enigma2/settings | grep "config.misc.backup_path"`
backuppath=${backupentry:24}

if [ -z $backupentry ]; then
	echo "Kein Pfad angegeben!"
	echo "Bitte den Pfad zum Ordner backup angeben!"
	echo "Wiederherstellung wird beendet"
	sleep 5
	exit 0
else
	backuppathcomp=$backuppath"backup"
	echo $backuppath
	echo ""
	echo "Backup wird von "$backuppathcomp
	echo "wieder hergestellt"
	echo ""
	backup=$backuppathcomp"/camsandconfigs.tar.gz"
	backupdo=$backup" -C /"

	if [ -e $backup ]; then
		tar -xzf $backupdo
		wait
		echo "Cams und Configs sind wiederhergestellt!"
		sleep 5
	else
		echo "Kann das Backup nicht wiederherstellen."
		echo ""
		exit 1
	fi
fi
