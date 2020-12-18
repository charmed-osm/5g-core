> ADD APACHE LICENCE
> IMPORTANT NOTE FOR ALL READMEs. RUN A MARKDOWN LINTING TOOL TO MAKE SURE THE FORMAT IS RIGHT
# 5G Core Operators

> Include a definition of what 5g Core is.

Consists of 12 applications
* db: short description  <-- This is mongodb in the bundle. Please change it here to mongodb
* nrf: short description
* amf: short description
* ausf  : short description
* nssf: short description
* pcf: short description
* udm: short description
* udr: short description
* webui: short description
* upf1: short description
* smf: short description
* natapp: short description

## Usage

### Prepare environment

> Add short explanatory sentence

```bash
sudo snap install microk8s --classic --channel 1.19/stable
microk8s.status --wait-ready
...
```

> Add short explanatory sentence

```bash
sudo snap install juju --classic --channel 2.8/stable
juju bootstrap microk8s
```

### Deploy

> Add short explanatory sentence

```bash
$ juju deploy cs:~tata-charmers/core  # <-- This should be pointing at the charm store bundle. All charms should be also in the charm store.
```

#### Deploy from local repository

> Add short explanatory sentence

```bash
git clone https://github.com/charmed-osm/5g-core
cd 5g-core/
```

> Add short explanatory sentence

```bash
microk8s.enable registry
```

> Add short explanatory sentence

```bash
./build_docker_images.sh  # <-- Create a script that install docker.io, that does the build of the docker images
docker push localhost:32000/ausf:1.0
docker push localhost:32000/nssf:1.0
...
...
```

> Add short explanatory sentence

```bash
./build_charms.sh  # <-- Create a script that builds the charms
```

> Add short explanatory sentence

```bash
juju add-model 5g-core
juju deploy ./bundle_local.yaml  # <-- Change the current bundle.yaml to bundle_local.yaml
```

### Integration

> This is incomplete. I'm expecting anyone to be able to execute the instructions needed to set up the microk8s.
> If metallb is needed, then add the instructions for it.
> If cross-model relations are needed between core and core, then add in both, core and ran repositories, the same consistent set of instructions. Also make a reference the other repo.
Core integration with RAN we have to expose LoadBalancer service for AMF,DB and UPF Component

## Testing

> Add short explanatory sentence

### Integration tests

> Add full and really clear instructions to execute zaza tests.

### Unit tests

> Add full and really clear instructions to execute unit tests.

## Get in touch

- Found a bug?: https://github.com/charmed-osm/5g-core/issues
- Email:
