#!/bin/sh
#PB-Powerboard-Team
#2013-06-11
#2014-10-29 rev B

case "$1" in
showonly)
    opkg update
    upgs=$(opkg list-upgradable | wc -l)
    if  [ "$upgs" != "0" ]
    then
        wget -s "http://127.0.0.1/web/message?text=%20$upgs%20updates%20available&type=1&timeout=0"
    else
        wget -s "http://127.0.0.1/web/message?text=%20No%20updates%20available&type=1&timeout=0"
    fi;;

update)
    var1=$(wget -O- -q http://127.0.0.1/web/timerlist | grep "<e2state>2</e2state>" | grep -cm 1 "2")
    if [ $var1 = "0" ]
    then
        wget -s "http://127.0.0.1/web/message?text=%20Performing%20update&type=1&timeout=0"
        init 4
        opkg update | opkg upgrade
        wait
        sync; sync; sync
        reboot -f
    else
        wget -s "http://127.0.0.1/web/message?text=%20Running%20recording%21%20Update%20by%20hand%21&type=1&timeout=0"
    fi;;
esac

