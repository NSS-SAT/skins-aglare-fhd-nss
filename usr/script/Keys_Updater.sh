#!/bin/bash

##DESCRIPTION=This script downloads latest CCcam keys & provider info.
softcam="https://raw.githubusercontent.com/MOHAMED19OS/SoftCam_Emu/main/SoftCam.Key"
echo ""
echo ""

if [ -f "/usr/keys/SoftCam.Key" ]; then
   rm -rf "/usr/keys/SoftCam.Key" > /dev/null 2>&1
fi
echo "Downloading ${softcam}"
wget --no-check-certificate -U 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36' -P '/usr/keys/' ${softcam} || echo "Error: Couldn't connect to ${softcam}"
echo ""
echo ""
echo "* Installed Successfully *"
echo "* E2 Restart Is Required *"
KeyDate=`/bin/date -r /usr/keys/SoftCam.Key +%d.%m.%y-%H:%M:%S`
	echo ""
	echo "UPDATE DATE AND TIME: $KeyDate"
	echo ""
exit 0
