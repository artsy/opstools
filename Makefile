test:
	pytest src/ecr_check_repos_for_terraform
	pytest src/kubernetes_cleanup_jobs
	pytest src/kubernetes_cleanup_namespaces
	pytest src/kubernetes_cleanup_pods
	# pytest src/kubernetes_export
	pytest src/lib
	# pytest src/rabbitmq_export_definitions
	pytest src/s3_prune_backups
	pytest src/terraform_drift_detection
