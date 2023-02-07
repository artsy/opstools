#!/bin/bash

# expect these params from env.
#
# check interval in seconds
# INTERVAL: 10
#
# dns servers to check against.
#
# k8s internal
# SERVER_K8S: 1.1.1.1
#
# aws vpc-internal
# SERVER_AWS: 2.2.2.2
#
# public dns server
# SERVER_PUBLIC: 3.3.3.3
#
# categories of domain names to check against.
#
# k8s cluster-internal dns name.
# DNS_K8S: a.b.c,d.e.f
#
# aws vpc-internal dns name.
# DNS_VPC: g.h.i
#
# your own public dns name.
# DNS_PUBLIC: j.k.l
#
# other's public dns name.
# DNS_OTHER: m.n.o

function check_udp() {
  local TIMEOUT=3
  local RETRY=0
  local NAME=$1
  local RESOLVER=$2
  local RETCODE=''
  dig +timeout=$TIMEOUT +retry=$RETRY $NAME @$RESOLVER > /dev/null
  RETCODE=$?
  [[ $RETCODE == 0 ]] || report $NAME $RESOLVER 'udp'
}

function check_tcp() {
  local TIMEOUT=3
  local RETRY=0
  local NAME=$1
  local RESOLVER=$2
  local RETCODE=''
  dig +tcp +timeout=$TIMEOUT +retry=$RETRY $NAME @$RESOLVER > /dev/null
  RETCODE=$?
  [[ $RETCODE == 0 ]] || report $NAME $RESOLVER 'tcp'
}

function report() {
  echo "dnstest: error on dns query for $1 against server $2 using $3"
}

while true
do
  # k8s internal
  names=`echo $DNS_K8S | tr "," "\n"`
  for name in $names
  do
    check_udp $name $SERVER_K8S
    check_tcp $name $SERVER_K8S
  done

  # artsy.systems
  names=`echo $DNS_VPC | tr "," "\n"`
  for name in $names
  do
    check_udp $name $SERVER_K8S
    check_tcp $name $SERVER_K8S
    check_udp $name $SERVER_AWS
    check_tcp $name $SERVER_AWS
  done

  # artsy.net
  names=`echo $DNS_PUBLIC | tr "," "\n"`
  for name in $names
  do
    check_udp $name $SERVER_K8S
    check_tcp $name $SERVER_K8S
    check_udp $name $SERVER_AWS
    check_tcp $name $SERVER_AWS
    check_udp $name $SERVER_PUBLIC
    check_tcp $name $SERVER_PUBLIC
  done

  # other
  names=`echo $DNS_OTHER | tr "," "\n"`
  for name in $names
  do
    check_udp $name $SERVER_K8S
    check_tcp $name $SERVER_K8S
    check_udp $name $SERVER_AWS
    check_tcp $name $SERVER_AWS
    check_udp $name $SERVER_PUBLIC
    check_tcp $name $SERVER_PUBLIC
  done

  sleep $INTERVAL
done

