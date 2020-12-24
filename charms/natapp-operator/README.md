<!-- Copyright 2020 Tata Elxsi

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

# Natapp

## Description

Kubernetes charm to deploy Natapp

## Prerequisite

1. Install Charmcraft

```bash
sudo snap install charmcraft --beta
```

## Usage

### Deploy

To deploy Natapp charm from Charmstore, use the following command

```bash
juju deploy cs:~tataelxsi-charmers/natapp
```

#### Deploy from local repository

To deploy Natapp from local repository, use the following commands

```bash
charmcraft build
juju deploy natapp.charm
```

NOTE: Natapp can be deployed only after UPF is up because of
      relations configured between the two.

## Developing

Check if the charm is deployed with juju status

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

   ./run_tests
