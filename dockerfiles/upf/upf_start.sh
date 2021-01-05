#!/bin/bash
ue_range=$(echo $UE_RANGE)
static_ip=$(echo $STATIC_IP)
echo 200 sr >> /etc/iproute2/rt_tables
ip rule add from $ue_range table sr
ip route add default via $static_ip dev eth1 table sr
ip route flush cache
sysctl -w net.ipv4.ip_forward=1
cd /free5gc/free5gc-upfd
./free5gc-upfd -f ../config/upfcfg.yaml
