# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##

FROM  opencord/quagga:latest

RUN apt-get update && apt-get install -y libpcap0.8 libnet-dev iptables
ADD NAT_App /NAT_App
WORKDIR /NAT_App
RUN echo '#!/bin/bash\n\
sysctl -w net.ipv4.ip_forward=1\n\
iptables -C OUTPUT -p tcp --tcp-flags RST RST -j DROP || iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP\n\
iptables -C OUTPUT -p icmp --icmp-type destination-unreachable -j DROP || iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP\n\
./nat eth1 eth0 169.254.1.1' > start.sh
RUN chmod +x start.sh

