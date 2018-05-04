#!/bin/sh
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
echo "Sichere Plugin-Liste!"
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
		var1=$(ipkg list-installed | grep enigma2-plugin-extension | cut -d" " -f1)
		echo $var1 >> /tmp/backuptmp/plugin-extensions.list
		wait
		var2=$(ipkg list-installed | grep enigma2-plugin-systemplugin | cut -d" " -f1)
		echo $var2 >> /tmp/backuptmp/plugin-system.list
		wait
		var3=$(ipkg list-installed | grep enigma2-skin | cut -d" " -f1)
		echo $var3 >> /tmp/backuptmp/skin.list
		wait
		cd /tmp/backuptmp
		chmod 666 plugin-extensions.list
		chmod 666 plugin-system.list
		chmod 666 skin.list
		wait
		backup=$backuppathcomp"/plugins.tar.gz *"
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