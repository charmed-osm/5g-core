# natapp

## Description

Kubernetes charm to deploy Natapp

## Usage

Natapp requires  port 


## Developing

Deploy the charm
juju deploy

Check if the charm is deployed with juju status

Check if the charm is deployed with juju status
To test 'iptables' action,run the following command
COMMAND : sudo juju run-action natapp/<UNIT-ID> iptables

To check the status and output of the action ,use the following command

COMMAND:
sudo juju show-action-status <ACTION-ID>
sudo juju show-action-output <ACTION-ID>

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
