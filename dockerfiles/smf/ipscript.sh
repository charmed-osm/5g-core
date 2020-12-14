#!/bin/bash

upf1=$(echo $IPADDR1)
find /free5gc/config/smfcfg.conf -type f -exec sed -i "s/upf1/$upf1/g" {} \;
#while true; do echo '.'; sleep 5 ; done
cd /free5gc/smf
./smf -smfcfg ../config/smfcfg.conf -uerouting ../config/uerouting.yaml
