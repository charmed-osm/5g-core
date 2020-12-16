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


## To build the charms and osm packages
* Build the charms enter into 5g-core/osm-packages/

  run ./build.sh

    The charms will be build, build and .charm can be located in respective operators inside charms directory.
Eg: build and amf.charm in 5g-core/charms/amf-operator,similarly in all charms it can be found.

* To create osm package and add necessary contents to it

   run ./package.sh
  
    Will generate osm packages placing all necessary contents and 
    finally a tar of vnf and ns
    * core_ns.tar.gz
    * core_vnf.tar.gz

   Onboard the resulting package to OSM
