test:
	pytest src/kubernetes_cleanup_jobs
	pytest src/kubernetes_cleanup_review_apps
	pytest src/kubernetes_cleanup_pods
	pytest src/kubernetes_configmap_jwt_scan
	pytest src/lib
	pytest src/terraform_drift_detection
