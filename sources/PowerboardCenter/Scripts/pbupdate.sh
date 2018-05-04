#!/bin/sh
#PB-Powerboard-Team
#2013-04-18

case "$1" in
showonly)
    var1=$(opkg update | opkg list-upgradable)
    var2="enigma2"
    if `echo ${var1} | grep "${var2}" 1>/dev/null 2>&1`
    then
        wget "http://127.0.0.1/web/message?text=Updates%20available&type=1&timeout=0"
    else
        wget "http://127.0.0.1/web/message?text=No%20updates%20available&type=1&timeout=0"
    fi;;

update)
    var1=$(wget -O- -q http://127.0.0.1/web/timerlist | grep "<e2state>2</e2state>" | grep -cm 1 "2")
    if [ $var1 = "0" ]
    then
        wget "http://127.0.0.1/web/message?text=Performing%20update&type=1&timeout=0"
        init 4
        opkg update | opkg upgrade
        wait
        reboot -f
    else
        wget "http://127.0.0.1/web/message?text=Running%20recording%21%20Update%20by%20hand%21&type=1&timeout=0"
    fi;;
esac
