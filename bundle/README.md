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

5G-Core is used to deploy a standalone working 5G Core setup. It is implemented
as microk8s applications using Juju Charms and Microk8s. It consists of the
following 12 components of 5G Core as charms,

* mongodb: Database of 5G Core
* nrf: Network Repository Function maintains an updated repository of all the 5g
       core components along with the services they provide
* amf: Access and Mobility Management Function is used in control plane
       interaction with RAN
* ausf: Authentication Server Function manages 5G UE authentication
* nssf: Network Selection Function used to select the network slice instance of
        5g components
* pcf: Policy Control Function provides policy based rules to control plane
       functions.
* udm: Unified Data Management manages user information in a centralized manner.
       Manages data for user registration, authorization and networks.
* udr: Unified Data Repository serves as a unified database for storing
       information about application, subscription and authentication.
* webui: User Interface for adding/removing IMSI information
* upf1: User Plane Function is used in data plane interaction with RAN
* smf: Session Management Function is used for interacting with data plane and
       creating and managing PDU sessions
* natapp: NAT application to enable data network accessibility

## Usage

### Prepare environment

#### A. Prerequisites

a. Linux Kernel Version

The Linux kernel version of `5.0.0-23-generic` is mandatory to use the UPF
component. To check the version of the existing Linux kernel,

```bash
uname -r
```

If the existing kernel version is not `5.0.0-23-generic`, then install it using,

```bash
sudo apt-get install linux-image-5.0.0-23-generic linux-headers-5.0.0-23-generic
```

For all popups just press enter with the option two selected. Then,

```bash
sudo reboot
```

b. Install Gtp5g module

* Gcc Installation:

     ```bash
     sudo apt update
     sudo apt install gcc
     sudo apt update
     sudo apt install make
     ```

* Clone Gtp5g Module:

     ```bash
     git clone https://github.com/PrinzOwO/gtp5g.git --branch v0.1.0
     ```

* Build:

     ```bash
     cd gtp5g
     make
     sudo make install
     ```

* Verification:

     ```bash
     lsmod | grep gtp5g
     ```

#### B. Install Microk8s

a. Install Microk8s using the following commands,

   ```bash
   sudo snap install microk8s --classic --channel 1.19/stable
   sudo usermod -a -G microk8s `whoami`
   newgrp microk8s
   microk8s.status --wait-ready
   ```

   The ouput "microk8s is running" signifies that Microk8s is successfully installed.

b. Enable the following required addons for Microk8s to deploy 5G Core

   ```bash
   microk8s.enable storage dns
   microk8s.enable multus
   microk8s.enable rbac
   ```

c. A configuration change is needed in the cluster for enabling SCTP traffic.

   ```bash
   vi /var/snap/microk8s/current/args/kube-apiserver
   //add the below line into the file
   --feature-gates="SCTPSupport=true"
   //Followed by stop and start of the cluster
   microk8s.stop
   microk8s.start
   ```

#### C. Install Juju

a. Install Juju with the following commands,

   ```bash
   sudo snap install juju --classic --channel 2.8/stable
   juju bootstrap microk8s
   ```

### Deploy

To deploy 5G Core from Charmstore, use the following command

```bash
juju deploy cs:~tata-charmers/core
```

#### Deploy from local repository

To deploy 5G Core from local repository, follow the steps below,

a. Clone the 5G-Core repository

   ```bash
   git clone https://github.com/charmed-osm/5g-core
   cd 5g-core/
   ```

b. Enable Microk8s registry for storing images

   ```bash
   microk8s.enable registry
   ```

c. Build 5G Core images

   ```bash
   ./build_docker_images.sh
   ```

d. Push built images to registry

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

e. Execute the following script to build all the 5G Core charms using Charmcraft,

   ```bash
   ./build_charms.sh
   ```

f. Create a model in Juju and deploy 5G Core,

   ```bash
   juju add-model 5g-core
   juju deploy ./bundle_local.yaml
   ```

### Integration

5G Core exposes its following services as loadbalancer services in order to
 facilitate control plane and data plane interactions with RAN,
   * AMF SCTP Service - For Control Plane User Registration and Attach Scenario.
   * MongoDB Service - For mongodb operations
   * UPF GTP Service - To enable data plane and data network accessbility to UE

In order to achieve this, 5G Core needs 3 Loadbalancer services to be exposed
 and published. This is done using,

```bash
microk8s.enable metallb
```

NOTE: 5G Core requires 3 loadbalancer IP addresses mandatorily.

## Testing

Run Integration and Unit tests to test and verify the 5G Core Charms.

### Integration tests

Functional tests for 5G Core were created using zaza.

#### Install tox

```bash
apt-get install tox
```

#### Run Integration Test

To run zaza integration test,

```bash
tox -e func_test
```

This command will create a model, deploy the charms, run tests and destroy the
model.

### Unit tests

Unit tests has to be executed in all the 5G Core components/charms.
The following commands show how to perform unit test in AMF,

```bash
cd charms/amf-operator
./run_tests
```

Similarly, unit tests can be run for all the other components/charms.

## Get in touch

Found a bug?: <https://github.com/charmed-osm/5g-core/issues>
Email: canonical@tataelxsi.onmicrosoft.com
