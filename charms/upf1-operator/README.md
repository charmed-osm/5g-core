<!--
 Copyright 2020 Tata Elxsi

 Licensed under the Apache License, Version 2.0 (the License); you may
 not use this file except in compliance with the License. You may obtain
 a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an AS IS BASIS, WITHOUT
 WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 License for the specific language governing permissions and limitations
 under the License.

 For those usages not covered by the Apache License, Version 2.0 please
 contact: canonical@tataelxsi.onmicrosoft.com

 To get in touch with the maintainers, please contact:
 canonical@tataelxsi.onmicrosoft.com
-->

# UPF1

## Description

Kubernetes charm to deploy UPF core component

Contains Juju action add-route which is used to configure of UPF interface.

## Prerequisite

1. Install Charmcraft

```bash
sudo snap install charmcraft --beta
```

## Usage

UPF exposes GTP port 2152 to integrate with RAN in the data plane.

### Deploy

To deploy UPF1 charm from Charmstore, use the following command

```bash
juju deploy cs:~tataelxsi-charmers/upf1 --resource image=tataelxsi5g/upf1:3.0
```

#### Deploy from local repository

To deploy UPF from local repository, use the following commands

```bash
charmcraft build
juju deploy ./upf1.charm
```

NOTE: UPF1 can be deployed only after Natapp is up because of
relations configured between the two.

## Developing

To test config-interface action,run the following command
COMMAND : juju run-action upf1/[UNIT-ID] config-interface

To check the status and output of the action ,use the following command

COMMAND:
juju show-action-status ACTION-ID
juju show-action-output ACTION-ID

Create and activate a virtualenv with the development requirements:

virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

./run_tests
