#!/bin/bash

docker build -t artsy/ops-util:dnstest .
docker push artsy/ops-util:dnstest
