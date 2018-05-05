PR .= ".1"
            
SRC_URI += " \
            file://mdev-mount.sh \
            "

FILESEXTRAPATHS_prepend := "${THISDIR}/${P}:"

