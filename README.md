# Opstools

Tools for Operations.

* __Point People:__ [#product-velocity][velocity_channel]

# Setup

Read and run the setup script:
```
./bin/setup
```

# Run Scripts

To run a script with environment files loaded (using [Foreman](https://github.com/ddollar/foreman)):

```
foreman run --env .env.shared,.env python src/...
```

# Testing

## Unit tests

```
make test
```

or

```
pytest <dir>
ptw <dir>
```

## Test scripts that interact with Staging/Production Kubernetes cluster

Some scripts (e.g. [kubernetes_export](./src/kubernetes_export)) interact with Staging/Production Kubernetes clusters. The scripts are usually run by Kubernetes as CronJobs that are tied to [`opstools` Kubernetes service account](https://github.com/artsy/substance/blob/main/clusters/staging/federation/kubernetes-staging-leo.artsy.systems/services/opstools-role.yml) which has the required permissions for the work.

When you test run the script locally, your `kubectl` authenticates to Kubernetes by [`KubernetesDev` IAM role](https://www.notion.so/artsy/Kubernetes-API-Authentication-and-Authorization-02bef8bbabf6468ba9ac6be7983300ac) which ultimately maps to permissions that are much more than that of `opstools` service account. Therefore, you may find that the script works locally but when run in Staging/Production, it lacks permissions.

To make local testing accurate, we have created a `KubernetesOpstools` IAM role which ultimately maps to the same permissions that `opstools` service account has. So before testing, switch your `kubectl` to `KubernetesOpstools` role as follows:

- Download `config-opstools` Kubeconfig file from S3 to `~/.kube` directory. See [setup script](./bin/setup).
- Symlink `~/.kube/config` to `~/.kube/config-opstools`.
- Run the script that you wish to test, for example:
  ```
  python src/kubernetes_export/export.py staging
  ```
- When done with testing, switch Kubeconfig back.

[velocity_channel]: https://artsy.slack.com/messages/product-velocity "#product-velocity Slack Channel"
