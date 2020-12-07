# db

## Description

Kubernetes charm to deploy Mongo DB

Possible action in this is adduser to mongodb

## Usage

Monodb port needed to be configured

## Developing

Deploy the charm
juju deploy

Check if the charm is deployed with juju status

To test dbinsert action,run the following command
COMMAND : sudo juju run-action db/<UNIT-ID> adduser ueid=<imsi-no>

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
