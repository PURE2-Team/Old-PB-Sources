#!/bin/sh
#Backup_all
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
echo "Sichere alle Punkte des Backups!"
echo ""
echo "Sichere Keys"
cd /usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts
./Backup_keys.sh
wait
echo "Sichere Cams und Configs"
cd /usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts
./Backup_camsandconfigs.sh
wait
echo "Sichere eine Liste der Plugins"
cd /usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts
./Backup_plugins.sh
wait
echo "Sichere Settings"
cd /usr/lib/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts
./Backup_settings.sh
wait
echo "Fertig!"
exit 0
