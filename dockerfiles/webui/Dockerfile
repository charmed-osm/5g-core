# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##

FROM free5gc/base:latest AS builder
FROM ubuntu:18.04

LABEL description="Free5GC open source 5G Core Network" \
    version="Stage 3"

ENV F5GC_MODULE webui
ARG DEBUG_TOOLS

# Install debug tools ~ 100MB (if DEBUG_TOOLS is set to true)
RUN if [ "$DEBUG_TOOLS" = "true" ] ; then apt-get update && apt-get install -y vim strace net-tools curl netcat-openbsd ; fi

# Set working dir
WORKDIR /free5gc
RUN mkdir -p config/ webconsole/public

# Copy executable, frontend static files and default configuration
COPY --from=builder /free5gc/${F5GC_MODULE} ./webconsole
COPY --from=builder /free5gc/public ./webconsole/public

# Move to the executable location
WORKDIR /free5gc/webconsole

# Config files volume
VOLUME [ "/free5gc/config" ]

# WebUI uses the port 5000
EXPOSE 5000
COPY webuicfg.conf /free5gc/config/webuicfg.conf
COPY free5GC.conf /free5gc/config/free5GC.conf
COPY webui_start.sh /free5gc/webconsole/webui_start.sh
RUN chmod +x /free5gc/webconsole/webui_start.sh
