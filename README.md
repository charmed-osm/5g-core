<!-- Copyright 2020 Tata Elxsi

 Licensed under the Apache License, Version 2.0 (the "License"); you may
 not use this file except in compliance with the License. You may obtain
 a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 License for the specific language governing permissions and limitations
 under the License.

 For those usages not covered by the Apache License, Version 2.0 please
 contact: canonical@tataelxsi.onmicrosoft.com

 To get in touch with the maintainers, please contact:
 canonical@tataelxsi.onmicrosoft.com
-->
# 5G Core Operators

Contains charm folder consisting of all 12 k8s charm applications


## Description

Consists of 12 applications
* db
* nrf
* amf
* ausf  
* nssf
* pcf
* udm  
* udr
* webui
* upf1
* smf
* natapp

## Usage
Build

sudo snap install charmcraft --beta

cd Application-operator
  
charmcraft build
  
Deploy

juju deploy ./juju-bundles/bundle.yaml

### Integration

Core integration with RAN we have to expose LoadBalancer service for AMF,DB and UPF Component
