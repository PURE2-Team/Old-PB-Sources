DESCRIPTION = "Powerboard Center"
PRIORITY = "optional"
LICENSE = "proprietary"
MAINTAINER = "Terrajoe"
PV = "7.0.0"
PR = "r11"

require conf/license/license-gplv2.inc

SRC_URI = "file://__init__.pyo \
           file://swap.pyo \
           file://plugin.pyo \
           file://spaceview.pyo \
           file://pbsetup.pyo \
           file://pbupdate.pyo \
           file://info.pyo \  
           file://keymap.xml \
           file://pics/* \
           file://Scripts/* \
           file://PBConfigs.pyo \
           file://PBDeviceManager.pyo \
           file://PBExpander.pyo \
           file://pbcamrestart.pyo \
           file://pbscriptstarter.pyo \
           file://PBTimeInput.pyo \
           file://PBCon.pyo \
           file://pbradio.pyo \
           file://pbdesign.pyo \
           file://pbplaylist \
           file://pbsender \
           file://PBnetinfo.pyo \
           file://pbremover.pyo \
           file://addonexpert.pyo \
           file://powerboard.png \
           file://pbabout.pyo \
           file://mountpb \
           file://mountpball \
           file://newsreader.pyo \
           file://pbswap \
           file://pbcamdinstaller.pyo \
           file://locale/*"
          
S = "${WORKDIR}"
FILES_${PN} = "${bindir}/* /etc/enigma2/*"
RDEPENDS_${PN} = "python-mutagen python-sqlite3 python-zlib pb2settings python-pyparted python-lxml enigma2-plugin-systemplugins-satfinder enigma2-plugin-extensions-easypbdevicemanager"
INHIBIT_PACKAGE_STRIP = "1"

sysroot_stage_all() {
    :
}

do_install () {
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pics
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/fhd
    install -d 755 ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/locale/de/LC_MESSAGES
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/locale/ru/LC_MESSAGES
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/locale/hr/LC_MESSAGES
    install -d ${D}/${bindir}
    install -d ${D}/etc/init.d
    install -d ${D}/etc/rcS.d
    install -d ${D}/etc/enigma2
    install    ${WORKDIR}/__init__.pyo  ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/__init__.pyo
    install    ${WORKDIR}/swap.pyo  ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/swap.pyo
    install    ${WORKDIR}/pbsetup.pyo   ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbsetup.pyo
    install    ${WORKDIR}/pbcamdinstaller.pyo   ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbcamdinstaller.pyo
    install    ${WORKDIR}/plugin.pyo    ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/plugin.pyo
    install    ${WORKDIR}/info.pyo  ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/info.pyo
    install    ${WORKDIR}/spaceview.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/spaceview.pyo
    install    ${WORKDIR}/PBConfigs.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/PBConfigs.pyo
    install    ${WORKDIR}/keymap.xml ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/keymap.xml
    install    ${WORKDIR}/powerboard.png ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/powerboard.png
    install    ${WORKDIR}/pbabout.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbabout.pyo
    install    ${WORKDIR}/pbupdate.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbupdate.pyo
    install    ${WORKDIR}/PBDeviceManager.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/PBDeviceManager.pyo
    install    ${WORKDIR}/PBExpander.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/PBExpander.pyo
    install    ${WORKDIR}/pbremover.pyo	${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbremover.pyo
    install    ${WORKDIR}/addonexpert.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/addonexpert.pyo
    install    ${WORKDIR}/newsreader.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/newsreader.pyo
    install    ${WORKDIR}/pbcamrestart.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbcamrestart.pyo
    install    ${WORKDIR}/PBTimeInput.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/PBTimeInput.pyo
    install    ${WORKDIR}/PBCon.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/PBCon.pyo
    install    ${WORKDIR}/pbradio.pyo      ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbradio.pyo
    install    ${WORKDIR}/pbdesign.pyo      ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbdesign.pyo
    install    ${WORKDIR}/pbsender         ${D}/etc/enigma2/pbsender
    install    ${WORKDIR}/pbplaylist       ${D}/etc/enigma2/pbplaylist
    install    ${WORKDIR}/PBnetinfo.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/PBnetinfo.pyo
    install    ${WORKDIR}/pbscriptstarter.pyo ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pbscriptstarter.pyo
    install    ${WORKDIR}/pics/*.png    ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/
    install    ${WORKDIR}/pics/fhd/*.png    ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/pics/fhd
    install    ${WORKDIR}/locale/PowerboardCenter.mo  ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/locale/de/LC_MESSAGES/ 
    install    ${WORKDIR}/locale/PowerboardCenter.moRU  ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/locale/ru/LC_MESSAGES/PowerboardCenter.mo
    install    ${WORKDIR}/locale/PowerboardCenter.moHR  ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/locale/hr/LC_MESSAGES/PowerboardCenter.mo  
    install    -m 0755 ${WORKDIR}/Scripts/* ${D}${libdir}/enigma2/python/Plugins/Extensions/PowerboardCenter/Scripts/
    install -m 0755 ${WORKDIR}/mountpb ${D}/${bindir}
    install -m 0755 ${WORKDIR}/mountpball ${D}/etc/init.d
    install -m 0755 ${WORKDIR}/pbswap ${D}/etc/init.d
    ln -s /etc/init.d/mountpball ${D}/etc/rcS.d/S55mountpball
    ln -s /etc/init.d/pbswap ${D}/etc/rcS.d/S60pbswap 
}

do_package_qa[noexec] = "1"

FILES_${PN} = "/"

