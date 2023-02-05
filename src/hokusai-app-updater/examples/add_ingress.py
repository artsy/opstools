import os

import argparse

YAML_SEPARATOR = '---'

EDIT_FILES = [
  'hokusai/staging.yml',
  'hokusai/staging.yml.j2',
  'hokusai/production.yml',
  'hokusai/production.yml.j2'
]

INTERNAL_SERVICE = """
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: svcName
    component: web
    layer: application
  name: svcName-web-internal
  namespace: default
spec:
  ports:
    - port: servicePort
      protocol: TCP
      name: http
      targetPort: servicePort
  selector:
    app: svcName
    layer: application
    component: web
  type: ClusterIP
"""

INGRESS = """
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: svcName
spec:
  rules:
    - host: hostName
      http:
        paths:
          - path: /
            backend:
              serviceName: svcName-web-internal
              servicePort: http

"""

INGRESS_CLOUDFLARE = """
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: svcName
  annotations:
    nginx.ingress.kubernetes.io/whitelist-source-range: "{{ cloudflareIpSourceRanges|join(',') }}"
spec:
  rules:
    - host: hostName
      http:
        paths:
          - path: /
            backend:
              serviceName: svcName-web-internal
              servicePort: http

"""

def main(projects):
  for project in projects:
    for file in EDIT_FILES:
      filename = os.path.join(project, file)
      if not os.path.isfile(filename):
        continue

      print("Editing %s ..." % filename)
      service_name = input("Enter the service name ( default: %s ) --> " % os.path.basename(project))
      if not service_name:
        service_name = os.path.basename(project)

      service_port = input("Enter the service port ( default: 8080 ) --> ")
      if not service_port:
        service_port = "8080"

      cloudflare = input("Is this service behond cloudflare? [y/n] --> ")
      if not cloudflare or cloudflare == 'n':
        ingress_template = INGRESS
      else:
        ingress_template = INGRESS_CLOUDFLARE

      hostname = input("Enter the hostname ( default: %s.artsy.net ) --> " % service_name)
      if not hostname:
        hostname = service_name + '.artsy.net'

      service = INTERNAL_SERVICE.replace('svcName', service_name).replace('servicePort', service_port)
      ingress = ingress_template.replace('svcName', service_name).replace('hostName', hostname)
      struct = None
      with open(filename, 'r') as f:
        struct = f.read()
      with open(filename, 'w') as f:
        f.write(struct)
        f.write(service)
        f.write(ingress)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Projects to update')
  parser.add_argument('projects', type=str, nargs='+')
  main(parser.parse_args().projects)
