#!/bin/sh
#
# 2013-03-16 ; PB-Team

# WORKS in Python but can't remove 'established' with busybox(es)
#           cmd10str = 'netstat -tpn |tail +3| cut -d" " -f 16-'
# watch possible bug in tail, maybe go with sed option (slower, more memory, but if it works...) 

case "$1" in
tcpinfo)
#set bold, oh yeah -  WISHFULL THINKING :)
#echo -e "\033[1m"
#set yellow
#echo -e "\033[33m"
        printf "%-24s %-24s %s\n\n" "Local Address" "Foreign Address" "PID/Program name"
#reset to normal (hopefuly...)
#echo -en "\033[0m"
# busybox version 
        netstat -tpn |tail +3|awk -F' '  '{printf "%-24s %-24s %s\n", $4, $5, $7}'
# coreutils version 
#        netstat -tpn |tail --lines=+3|awk -F' '  '{printf "%-24s %-24s %s\n", $4, $5, $7}'
        ;;

general)
        printf "\n%s\n" "Some info about your network :"
        privateIP=$(ifconfig |grep 'inet addr:'|grep -v '127.0.0.1'|cut -d: -f2|awk '{print$1}')
        macADR=$(ifconfig |grep 'HWaddr'| awk '{print$5}')
        mtuSIZE=$(ifconfig |grep 'CAST  MTU:'|cut -d: -f2|cut -d' ' -f1)
        rxBytes=$(ifconfig |grep 'RX bytes:'|cut -d : -f 2|cut -dT -f1|head -n 1)
        txBytes=$(ifconfig |grep 'RX bytes:'|cut -d : -f 3|head -n 1)
        gatewayIP="$(netstat -rn|grep 'UG'|awk '{print$2}')" 
        publicIP="$(wget -q -O - http://checkip.dyndns.org|sed -e 's/.*Current IP Address: //' -e 's/<.*$//')"
        ofoSEG="$(dmesg|grep 'ofo' -c)"        
#add if rx && tx == 0 we have either net down or WiFi, can be under wlan0, ra0 and some third wifi name...
        printf "\n%-35s %-20s\n"  "Local IP address is :" "$privateIP"
        printf "%-35s %-20s\n"  "Public IP address is :" "$publicIP"
        printf "%-35s %-20s\n"  "Gateway/Router IP address is :" "$gatewayIP"
        printf "%-35s %-20s\n"  "MAC of your STB is :" "$macADR"
        printf "%-35s %-20s\n"  "Received bytes so far :" "$rxBytes"
        printf "%-35s %-20s\n"  "Sent bytes so far :" "$txBytes"
        printf "%-35s %-20s\n"  "Max transmission unit :" "$mtuSIZE"
        printf "%-35s %-20s\n"  "Out of order segments :" "$ofoSEG"
        if [[ "$ofoSEG" -gt 015 ]]; then
            printf "\n%s\n" "Note: many 'Out of order segments' errors could be CCcam related."
        fi
        ;;

speed)
# samples at http://www.thinkbroadband.com/download.html seem to fast and available
# set -x
# get time 
        printf "%s\n\n" "Please be patient for a while, checking download speed..."
        timeStart=$(date +%s)
        wget -q -O/dev/null http://download.thinkbroadband.com:81/10MB.zip
        timeEnd=$(date +%s)
        time_diff=$(( $timeEnd - $timeStart ))
        rx_size=10485760
# does it make any sense ? If so rx_rate hold bytes/sec
        if [[ "${time_diff}" -gt 0 ]]; then
          rx_rate=$(( $rx_size / $time_diff ))
        fi
# shift by 10 bytes to get KiB/s and by 20 for MiB/s
# and print the more human readable value.
        rx_kib=$(( $rx_rate >> 10 ))
        printf "%s %i %s\n" "Approximate download speed is: " "${rx_kib}" " KiB/second"
        
        printf "\n%s\n\n" "Please be patient for a while, checking ping response..."
# Start timing again         
        timeStart=$(date +%s)
#        ping -q -w 10 google.de > "/tmp/pResult.tmp"           
        ping -q -w 10 google.de > "/tmp/pResult.tmp"           
#        cat "/tmp/pResult.tmp"|tail --lines=+3
        cat "/tmp/pResult.tmp"|tail -n +3
        gatewayIP="$(netstat -rn|grep 'UG'|awk '{print$2}')"
        printf "\n%s\n" "Checking ping to your router ..."
        ping -q -w 5 "$gatewayIP" > "/tmp/pResult.tmp"
#        cat "/tmp/pResult.tmp"|tail --lines=+3
        cat "/tmp/pResult.tmp"|tail -n  +3

        rm "/tmp/pResult.tmp"

#        timeEnd=$(date +%s)
#        time_diff=$(( $timeEnd - $timeStart ))
#        rx_rate=$(( $rx_size / $time_diff ))
#        rx_kib=$(( $rx_rate >> 10 ))
#        printf "%s %i %s\n" "Approximate download speed for mesured while pinging is: " "${rx_kib}" " KiB/second"
        ;;

misc)
        printf "%-24s %-24s %s\n\n" "Not used" "at the moment" "dummy placeholder" 
        ;;
        
esac

