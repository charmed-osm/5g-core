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
microk8s.enable metallb
```

NOTE: 5G Core requires 3 loadbalancer IP addresses mandatorily. So allocate 3
IP addresses while enabling metallb.

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

To deploy 5G Core from Charmstore, use the following steps

a. Deploy core applications

```bash
juju deploy cs:~tataelxsi-charmers/core-5g
```

b. Configuring interface

For the deployment to get completed successfully, update master_interface field
to your server's main interface name with the following command,

```bash
juju config natapp master_interface="<interface_name>"
```

where interface_name stands for server's main interface name where core is
deployed

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

g. Configuring interface

For the deployment to get completed successfully, update master_interface field
to your server's main interface name with the following command,

```bash
juju config natapp master_interface="<interface_name>"
```

where interface_name stands for server's main interface name where core is
deployed

### Integration

5G Core exposes its following services as loadbalancer services in order to
facilitate control plane and data plane interactions with RAN,

* AMF SCTP Service - For Control Plane User Registration and Attach Scenario.
* MongoDB Service - For mongodb operations
* UPF GTP Service - To enable data plane and data network accessbility to UE

In order to achieve this, 5G Core needs 3 Loadbalancer services to be exposed
and published. This is done using the below command,

```bash
microk8s.enable metallb
```

NOTE: 5G Core requires 3 loadbalancer IP addresses mandatorily. Ignore this
step if already done in pre-requisites.

#### Juju Actions

a. Action "config-interface" in UPF1 to configure the MTU size of the
upfgtp0 interface of UPF application,

```bash
juju run-action upf1/<unit_id> config-interface
```

where unit_id is the Unit number of the deployed application.

b. Action "add-user" in mongodb to add subscriber information to core,

```bash
juju run-action mongodb/<unit_id> add-user ue-id=<IMSI_Number>
```

where unit_id is the Unit number of the deployed application,
IMSI_Number is the IMSI number of the subscriber to be added in 5G-Core.
imsi-2089300007487 is an example of IMSI number format.

After executing each action, an ID will be generated like below,
Action queued with id: "ID"
This ID can be used to check the action status using the following command,

```bash
juju show-action-output <ID>
```

Check for the status of the action in the output which should be "completed".

#### Actions Verification

a. "config-interface" in upf1 has to be verified with the following command,

```bash
ifconfig
```

Check for the MTU size of upfgtp0 interface which would have been set to 1440.

b. To verify “add-user”, login to mongodb application pod and verify the
successful addition of imsi number,

```bash
mongo mongodb://db/free5G use free5gc
show collections
db.policyData.ues.amData.find()
```

where the imsi number added can be found under under key ueid.

### 5G Scenarios

#### 5G User Registration

After 5G-Core and 5G-RAN(https://github.com/charmed-osm/5g-ran) are deployed and
actions are completed, the user registration can be triggered through the
following rest API call with POST method,

```bash
http://ran-loadbalancerip:8081/attachtrigger/1
```

> Sample response for successful attach,
> Response Message: "Triggered Attach for the requested UE!"
> Response Code: 200 OK

#### Internet Traffic Flow

Once registration is successful, 5G-RAN's UE application would be enabled to
access the data network. Test the following in UE application,

a. ICMP TRAFFIC

```bash
ping 8.8.8.8
```

b. TCP TRAFFIC

```bash
wget google.com
```

c. UDP TRAFFIC

```bash
nc -u <netcat server-ip> port
```

where netcat server-ip is the IP address of the server where netcat server is
running.
Note: for UDP traffic netcat server should be running in another server. To do
that use the following commands in another server.

```bash
apt-get install netcat
nc -u -l -p <any unused port>
```

#### Voice Traffic Flow

Voice traffic flow can be tested once 5G-Core,
5G-RAN(https://github.com/charmed-osm/5g-ran) and
5G-IMS(https://github.com/charmed-osm/5g-ims) are deployed and actions are
completed. To test voice traffic flows, a SIP client called PJSIP is already
installed in the UE application. Follow the below steps in UE application,

a. Traverse to /pjproject directory in the UE pod.

b. alice.cfg is configured for an user named alice which is already available
in IMS by default.

Note: The username, password and id can be changed to any user added from day-2
action of IMS as well.

c. Add the following content to /etc/hosts file,

> <PCSCF_LB_IP> mnc001.mcc001.3gppnetwork.org
> <PCSCF-LB_IP> pcscf.mnc001.mcc001.3gppnetwork.org

Where <PCSCF-LB_IP> is the loadbalancer IP of PCSCF application and
mnc001.mcc001.3gppnetwork.org is the domain added in coredns of IMS cluster.

d. Execute the following command to register the user alice with IMS,

```bash
pjsua --config-file alice.cfg --log-level=3
```

Note: Peform the above steps in another server to register another user say bob
with IMS so that SIP calls can be tested between the two users.

e. After registration of both users, press ‘m’ from UE application's alice
and then press enter to initiate a SIP call.

f. Give bob’s id and then press enter. The message “Calling”
can be observed in alice’s UE pod.

g. Then in bob’s server, the following message can be seen,

> Press ‘a’ to answer or ‘h’ to hangup

h. Press a and then enter. Then the following message will be displayed,

> Answer with code:

i. Type 200 and enter.

j. After this “Confirmed” message can be seen in both alice and bob
indicating that the call between alice and bob is successful and that RTP
packets are being sent between alice and bob. The same can be verified by
capturing SIP packets using ngrep, tcpdump or wireshark.

k. Then to end/hangup the call, press h and then enter from alice. Verify the
“Disconnected” message in both alice and bob.

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
