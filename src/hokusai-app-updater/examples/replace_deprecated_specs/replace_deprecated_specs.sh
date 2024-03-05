#!/bin/bash

# Depends on GNU-sed installed as gsed (via `brew install gnu-sed`).

deprecations=(
  "apiVersion: batch/v1beta1"
  "apiVersion: networking.k8s.io/v1beta1"
  "              serviceName: "
  "              servicePort: "
  "            serviceName: "
  "            servicePort: "
  "          serviceName: "
  "          servicePort: "
)

replacements=(
  "apiVersion: batch/v1"
  "apiVersion: networking.k8s.io/v1"
  "              service:\n                name: "
  "                port:\n                  name: "
  "            service:\n              name: "
  "              port:\n                name: "
  "          service:\n            name: "
  "            port:\n              name: "
)

for i in "${!deprecations[@]}"; do
  echo "Replacing '${deprecations[i]}' with '${replacements[i]}'"

  for file in `find . -name "staging.yml*"`
  do
    echo $file
    gsed -z -i -e "s|${deprecations[i]}|${replacements[i]}|g" $file
  done

  for file in `find . -name "production.yml*"`
  do
    echo $file
    gsed -z -i -e "s|${deprecations[i]}|${replacements[i]}|g" $file
  done
done


