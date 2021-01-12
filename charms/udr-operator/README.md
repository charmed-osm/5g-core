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

# UDR

## Description

Kubernetes charm to deploy UDR core component

## Prerequisite

1. Install Charmcraft

```bash
sudo snap install charmcraft --beta
```

## Usage

### Deploy

To deploy UDR charm from Charmstore, use the following command

```bash
juju deploy cs:~tataelxsi-charmers/udr
```

#### Deploy from local repository

To deploy UDR from local repository, use the following commands

```bash
charmcraft build
juju deploy ./udr.charm
```

NOTE: UDR can be deployed only after NRF is up because of
relations configured between the two.

## Developing

Create and activate a virtualenv with the development requirements:

virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

./run_tests
