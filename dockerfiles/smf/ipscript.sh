#!/bin/bash
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


upf1=$(echo $IPADDR1)
nrf_app_name=$(echo $NRF_HOST)
find /free5gc/config/smfcfg.conf -type f -exec sed -i "s/upf1/$upf1/g" {} \;
sed -i "s~\<nrf_app\>~$nrf_app_name~g" /free5gc/config/smfcfg.conf
#while true; do echo '.'; sleep 5 ; done
cd /free5gc/smf
./smf -smfcfg ../config/smfcfg.conf -uerouting ../config/uerouting.yaml
