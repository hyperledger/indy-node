#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

FROM ubuntu:16.04

MAINTAINER Andrey Zheregelya

# Currently this file contains the copy of validator node but without database config.
# It also starts CLI as entrypoint by default
# And also contains tester script

ARG install_indy_common="pip3 install --no-cache-dir indy-common"
ARG install_indy_client="pip3 install --no-cache-dir indy-client"

RUN apt-get update \
    && apt-get install python3.5 libsodium18 libgmp3-dev flex bison libssl-dev bsdmainutils python3-pip -y \
    && apt-get install wget -y \
    && apt-get install git -y \
    && apt-get clean

# TODO: use native packages when they will be ready.
RUN wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz \
    && tar xvf pbc-0.5.14.tar.gz \
    && cd pbc-0.5.14 \
    && ./configure && make && make install \
    && cd .. && rm -rf pbc-0.5.14 pbc-0.5.14.tar.gz

RUN pip3 install --upgrade pip wheel setuptools \
    && pip3.5 install Charm-Crypto==0.43 \
    && $install_indy_common \
    && $install_indy_client

ENTRYPOINT ["indy"]
