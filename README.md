# 5G Core Operators

Contains charm folder consisting of all 12 k8s charm applications


## Description

Consists of 12 applications
* db
* nrf
* amf
* ausf  
* nssf
* pcf
* udm  
* udr
* webui
* upf1
* smf
* natapp

## Usage
Build

sudo snap install charmcraft --beta

cd <Application-operator>
  
charmcraft build
  
Deploy

juju deploy ./juju-bundles/bundle.yaml

### Integration

Core integration with RAN we have to expose LoadBalancer service for AMF,DB and UPF Component
