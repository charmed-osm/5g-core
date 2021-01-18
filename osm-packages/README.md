<!--
Copyright 2020 Tata Elxsi

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

# Create and Onboard 5g-core osm packages

> To create osm vnf and ns packages, use the following commands which will
> generate a vnf package structure named core_vnf and ns package structure
> named core_ns

```bash
osm package-create vnf core
osm package-create ns core
```

> Copy the desriptor into corresponding directory

```bash
cp core_vnfd.yaml core_vnf/
cp core_nsd.yaml core_ns/
```

> To onboard packages into OSM, use the following commands

```bash
osm nfpkg-create core_vnf
osm nspkg-create core_ns
```

> Onboarded packages can be verified with the following commands

```bash
osm nfpkg-list
osm nspkg-list
```

# Adding vim-account and k8scluster to OSM

## Vim-Account

```bash
osm vim-create --name <vim_name> --user <username> --password <password> --auth_url
<openstack-url> --tenant <tenant_name> --account_type openstack
```

vim-create command helps to add vim to OSM where,

* "vim_name" is the name of the vim being created.
* "username"and "password" are the credentials of Openstack.
* "tenant_name" is the tenant to be associated to the user in the Openstack.
* "openstack-url" is the URL of Openstack which will be used as VIM.

## K8sCluster

```bash
osm k8scluster-add --creds <kube.yaml> --version '1.19' --vim <vim_name>
--description "CORE Cluster" --k8s-nets '{"net1": "<network-name>"}' <cluster_name>
```

K8scluster add helps to attach a cluster with OSM which will be used for knf deployment.
where,

* "kube.yaml" is the configuration of microk8s cluster obtained from "microk8s config>kube.yaml".
* "vim_name" is the vim created in the last setup.
* "cluster_name" a unique name to identify your cluster.

Note:[Prerequisites and microk8s setup for 5g-core](../README.md)

# Launching the 5g-core

```bash
osm ns-create --ns_name core --nsd_name core_nsd --vim_account <vim_name>
```

> ns-create will instantiate the 5g-core network service use
> "vim_name" thats added to osm.

## Verifying the services

```bash
osm ns-list
```

> Will display the ns-created with ns-id, with status active and configured
> which means the service is up along with its day1 operations.

```bash
osm ns-show
```

> Will show detailed information of the network service.

```bash
microk8s kubectl get all –n core-kdu-<ns-id>
```

> will dispaly all 12 components deployed from bundle in vnfd.

## 5g-core day2 operation

```bash
osm ns-action core --vnf_name 1 --kdu_name core-kdu --action_name
add-user --params '{application-name: mongodb,ue-id: imsi-2089300007487 }'
```

* where "core" is the network service name, "1" points to vnf member index
  and "core-kdu" is the kdu name used in package.

* "ueid" parameter should hold the desired imsi number.
