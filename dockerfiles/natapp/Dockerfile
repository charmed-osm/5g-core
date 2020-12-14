FROM  ubuntu:18.04

RUN apt-get update && apt-get install -y libpcap0.8 libnet-dev iptables
ADD NAT_App /NAT_App
WORKDIR /NAT_App
RUN echo '#!/bin/bash\n\
sysctl -w net.ipv4.ip_forward=1\n\
iptables -C OUTPUT -p tcp --tcp-flags RST RST -j DROP || iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP\n\
iptables -C OUTPUT -p icmp --icmp-type destination-unreachable -j DROP || iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP\n\
./nat eth1 eth0 169.254.1.1' > start.sh
RUN chmod +x start.sh

