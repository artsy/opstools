# initialize the app
from kubernetes_configmap_jwt_scan.config import config

from kubernetes_configmap_jwt_scan.scan import scan

if __name__ == "__main__":

  scan()
