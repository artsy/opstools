test:
	pytest src/kubernetes_cleanup_namespaces
	pytest src/kubernetes_cleanup_pods
	pytest src/kubernetes_cleanup_jobs
	pytest src/lib
	pytest src/terraform_drift_detection
