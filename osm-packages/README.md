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

> As all the charms and the bundle will be in the charm store, you do not need all this.
> Add two folders ready to be uploaded to osm:
 - nsd
 - vnfd <-- in the juju-bundle, point to the charm store

> ^ the package.sh can be put as clear, simple, and complete instructions here in the readme. Remove the package.sh then.

> In the readme, add the commands needed to upload the packages: osm nfpkg-create, and nspkg-create.

> Also add the steps to onboard it to OSM.

> Add an integration part in the end, saying how would you integrate it in OSM with ran and IMS.

> Cross-model relations are not supported yet in OSM, so add the manual instructions to set up the cross-model relations