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

FROM golang:1.14.4-stretch AS builder

LABEL maintainer="Free5GC <support@free5gc.org>"

RUN apt-get update
RUN apt-get -y install gcc cmake autoconf libtool pkg-config libmnl-dev libyaml-dev
RUN apt-get clean

# Get Free5GC
RUN cd $GOPATH/src \
    && git clone --recursive -b v3.0.3 -j 33 https://github.com/free5gc/free5gc.git \
    && cd free5gc \
    && go mod download

# Build NF (AMF, AUSF, N3IWF, NRF, NSSF, PCF, SMF, UDM, UDR)
RUN cd $GOPATH/src/free5gc/src \
    && for d in * ; do if [ -f "$d/$d.go" ] ; then CGO_ENABLED=0 go build -a -installsuffix nocgo -o ../bin/"$d" -x "$d/$d.go" ; fi ; done ;

# Build UPF
#RUN go get -u -v "github.com/sirupsen/logrus"
RUN cd $GOPATH/src/free5gc/src/upf \
    && mkdir -p build \
    && cd build \
    && cmake .. \
    && make -j `nproc`

# Build WebUI
RUN cd $GOPATH/src/free5gc/webconsole \
    && CGO_ENABLED=0 go build -a -installsuffix nocgo -o webui -x server.go

# Alpine is used for debug purpose. You can use scratch for a smaller footprint.
FROM alpine

WORKDIR /free5gc
RUN mkdir -p config/ support/TLS/ public

# Copy executables
COPY --from=builder /go/src/free5gc/bin/* ./
COPY --from=builder /go/src/free5gc/src/upf/build/bin/* ./
COPY --from=builder /go/src/free5gc/webconsole/webui ./

# Copy static files (webui frontend)
COPY --from=builder /go/src/free5gc/webconsole/public ./public

# Copy linked libs
COPY --from=builder /go/src/free5gc/src/upf/build/libgtp5gnl/lib/libgtp5gnl.so.0 ./
COPY --from=builder /go/src/free5gc/src/upf/build/utlt_logger/liblogger.so ./

# Copy configuration files (not used for now)
COPY --from=builder /go/src/free5gc/config/* ./config/
COPY --from=builder /go/src/free5gc/src/upf/build/config/* ./config/

# Copy default certificates (not used for now)
COPY --from=builder /go/src/free5gc/support/TLS/* ./support/TLS/
