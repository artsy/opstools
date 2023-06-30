from kubernetes_export.export import export_and_backup

if __name__ == "__main__":

  KUBERNETES_OBJECTS = [
    'configmaps',
    'cronjobs',
    'daemonsets',
    'deployments',
    'horizontalpodautoscalers',
    'ingresses',
    'persistentvolumeclaims',
    'poddisruptionbudgets',
    'replicationcontrollers',
    'rolebindings',
    'roles',
    'secrets',
    'serviceaccounts',
    'services',
    'statefulsets'
  ]
  export_and_backup(KUBERNETES_OBJECTS)
