test:
	pytest src/kubernetes_cleanup_namespaces
	pytest src/kubernetes_cleanup_pods_by_name
	pytest src/lib
	pytest src/terraform_drift_detection
