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

ENV F5GC_MODULE free5gc-upfd
ENV DEBIAN_FRONTEND noninteractive
ARG DEBUG_TOOLS

# Install debug tools ~ 100MB (if DEBUG_TOOLS is set to true)
RUN if [ "$DEBUG_TOOLS" = "true" ] ; then apt-get update && apt-get install -y vim strace net-tools iputils-ping curl netcat ; fi

# Install UPF dependencies
RUN apt-get update \
    && apt-get install -y libmnl0 libyaml-0-2 iproute2 iptables python3.8 net-tools\
    && apt-get clean

# Set working dir
WORKDIR /free5gc
RUN mkdir -p ${F5GC_MODULE}/config/

# Copy executable and default configuration
COPY --from=builder /free5gc/${F5GC_MODULE} ./${F5GC_MODULE}/

# Copy linked libs
COPY --from=builder /free5gc/libgtp5gnl.so.0 /usr/local/lib
COPY --from=builder /free5gc/liblogger.so /usr/local/lib

# Move to the executable location
WORKDIR /free5gc/${F5GC_MODULE}
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2

# Update links
RUN ldconfig
COPY upfcfg1.yaml /free5gc/config/upfcfg.yaml
COPY upf_start.sh /free5gc/${F5GC_MODULE}/upf_start.sh
RUN chmod +x /free5gc/${F5GC_MODULE}/upf_start.sh
