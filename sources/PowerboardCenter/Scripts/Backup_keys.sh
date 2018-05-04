#!/bin/sh
#DESCRIPTION=Erstellt ein Backup der Keys in /usr/keys auf CF!
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
echo "Sichere Keys!"

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
		backup=$backuppathcomp"/keysbackup.tar.gz /usr/keys/*"
		echo "Erstellt Backup-tarball..."
		tar -czf $backup
		wait
		chmod 666 $backuppathcomp"/keysbackup.tar.gz"
		wait
		echo "Backup-tarball erstellt."
	else
		echo "Kann kein Backup anlegen."
	fi
	echo ""
fi
exit 0
