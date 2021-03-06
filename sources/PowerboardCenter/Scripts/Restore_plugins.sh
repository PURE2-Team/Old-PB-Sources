#!/bin/sh
#DESCRIPTION=Lese alte Plugins aus und installiere neueste Version vom Server!
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
echo "Lese alte Plugins aus und installiere neueste Version vom Server!"
echo 
echo "Wenn vorhanden werden Plugins aus dem Ordner"
echo "plugins_important"
echo "mit installiert!"
echo ""

#und ab daf�r...
echo "Lade Pluginliste vom Server"
opkg update
wait
mkdir /tmp/backuptmp
imp=`find / -type d -name plugins_important`
if [ -z $imp ]; then
	echo "Kein Ordner plugins_important gefunden"
else
	echo "Ordner wurde gefunden"
	echo "installiere Erweiterungen aus"
	echo $imp
	echo "oder, wenn vorhanden, neuere Version vom Server"
	pluginst=$(ls $imp)
	cd $imp
	opkg install $pluginst
	echo "Erweiterungen sind installiert"
	wait
fi

echo "Nun die gesicherten Plugins und Skins..."
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
	echo "Liste auslesen von "$backuppathcomp
	echo ""
	backup=$backuppathcomp"/plugins.tar.gz"
	backupdo=$backup" -C /tmp/backuptmp"

	if [ -e $backup ]; then
		tar -xzf $backupdo
	fi
fi

if [ -e /tmp/backuptmp/plugin-system.list ];then
	echo "Installation der Erweiterungen und/oder Skins vom Server"
	var1=$(cat /tmp/backuptmp/plugin-system.list)
	var2=$(cat /tmp/backuptmp/plugin-extensions.list)
	var3=$(cat /tmp/backuptmp/skin.list)
	wait
	opkg install $var1
	wait
	opkg install $var2
	wait
	opkg install $var3
	wait
	rm -fr /tmp/backuptmp
	wait
	echo "Installation abgeschlossen"
	echo "Starte Enigma2 neu um die Plugins in den Men�s anzuzeigen!"
	sleep 5
	wget -q -O - http://127.0.0.1/web/powerstate?newstate=3
else
	echo "Kann das Backup nicht wiederherstellen."
	echo ""
	exit 1
fi
