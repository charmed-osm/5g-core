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
# mongodb

## Description

Kubernetes charm to deploy Mongo DB

Possible action in this is adduser to mongomongodb

## Usage

Mongodb port needed to be configured

## Developing

Deploy the charm
juju deploy

Check if the charm is deployed with juju status

To test mongodb insert action,run the following command
COMMAND : sudo juju run-action mongodb/<UNIT-ID> adduser ueid=<imsi-no>

To check the status and output of the action ,use the following command

COMMAND:
sudo juju show-action-status <ACTION-ID>
sudo juju show-action-output <ACTION-ID>


Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
