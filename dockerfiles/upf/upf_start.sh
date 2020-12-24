#!/bin/bash

echo 200 sr >> /etc/iproute2/rt_tables
ip rule add from 60.60.0.0/24 table sr
ip route add default via 192.168.1.216 dev eth1 table sr
ip route flush cache
sysctl -w net.ipv4.ip_forward=1
cd /free5gc/free5gc-upfd
./free5gc-upfd -f ../config/upfcfg.yaml
