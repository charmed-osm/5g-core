# upf1

## Description

Kubernetes charm to deploy UPF core component

## Usage

UPF requires UDP port , TCP port 

## Developing

Deploy the charm
juju deploy

Check if the charm is deployed with juju status

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt


## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests

