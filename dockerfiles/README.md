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

# 5G-Core dockerfiles

The current directory holds the dockerfiles for core components

## Description

Consists of 12 components dockerfiles, 1 base dockerfile and a base Makefile.

### Base Dockerfile and Makefile

Used to build the free5gc base image. This image would be
used as base image to build all the free5gc components.

### Component Dockerfiles

* amf
* ausf
* natapp
* mongodb
* nrf
* nssf
* pcf
* smf
* udm
* udr
* upf
* webui

## Usage

To build images of all the 5G Core Components,

```bash
cd ..
./build_docker_images.sh
```

To push the built images to registry,

```bash
docker push localhost:32000/free5gc-mongo:1.0
docker push localhost:32000/free5gc-nrf:1.0
docker push localhost:32000/free5gc-amf:1.0
docker push localhost:32000/free5gc-ausf:1.0
docker push localhost:32000/free5gc-nssf:1.0
docker push localhost:32000/free5gc-udm:1.0
docker push localhost:32000/free5gc-udr:1.0
docker push localhost:32000/free5gc-pcf:1.0
docker push localhost:32000/free5gc-upf-1:1.0
docker push localhost:32000/free5gc-webui:1.0
docker push localhost:32000/free5gc-smf:1.0
docker push localhost:32000/free5gc-natapp:1.0
```

## Exposed Ports

----------------------------------------------------------
|     NF       |   Exposed Ports  | Dependencies         |
----------------------------------------------------------
|    amf       |      29518       |   nrf                |
----------------------------------------------------------
|    ausf      |      29509       |   nrf                |
----------------------------------------------------------
|    nrf       |      29510       |   mongodb            |
----------------------------------------------------------
|    nssf      |      29531       |   nrf                |
----------------------------------------------------------
|    pcf       |      29507       |   nrf                |
----------------------------------------------------------
|    smf       |      29502       |   nrf, upf           |
----------------------------------------------------------
|    udm       |      29503       |   nrf                |
----------------------------------------------------------
|    udr       |      29504       |   nrf, mongodb       |
----------------------------------------------------------
|    upf       |      N/A         |   pfcp,gtpu,apn      |
----------------------------------------------------------
|   webui      |      5000        |   mongodb            |
----------------------------------------------------------
|   mongodb    |      27017       |   N/A                |
----------------------------------------------------------
|   natapp     |      N/A         |   upf                |
----------------------------------------------------------
