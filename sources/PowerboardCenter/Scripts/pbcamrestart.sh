#!/bin/sh
#PB-Powerboard-Team
#2013-06-16


CAMACT=$(cat /etc/clist.list)
CAMSKRIPTHelper=$(grep "${CAMACT}" /usr/script/cam/*)
CAMSKRIPTHelper2=$(echo ${CAMSKRIPTHelper%:*})
CAMSKRIPT=$(echo ${CAMSKRIPTHelper2##*/})
CAMANZ=$(echo ${CAMSKRIPT%.*})
RES=$(echo $CAMSKRIPT" cam_res")

while wget -O- -q http://127.0.0.1/web/timerlist |grep "<e2state>2</e2state>" |grep -m 1 "2" |grep "2" |sed 's/.*<e2state>\(.*\)<\/e2state.*/\1/'| grep "2"
    do sleep 300
done
cd /usr/script/cam
./$RES
wget "http://127.0.0.1/web/message?text="$CAMANZ"%20restarted&type=1&timeout=10"

exit 0
