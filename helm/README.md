# MediaThread Helm Chart

This is a Helm chart used for a Kubernetes (K8s) deployment of MediaThread. It uses the docker container built from this same repository.

This is an early build and is not at feature parity with the base deployment.

TODO list:

* Expose mechanisms for customizations via `deploy\_specific`
* Integrate Nginx/HTTPd frontend


## Configuration

All values in [values.yaml](values.yaml) will be treated as default values. They can be overridden during deploy with helm's `--set` parameter. Subsequent Helm upgrades will carry over previous `--set` parameters unless `--reset-values` is also specified, which will then default to values in values.yaml.

ALLOWED\_HOSTS value **must contain** the `kube-healthcheck.cluster.local` value as one of its entries. This host header is used by Kubernetes' internal liveness/readiness probes as defined further within this chart. 

A database is **NOT** included in this chart. A PostgreSQL or compatible database is required.
Therefore the `env.DB\_*` parameters are required to be populated and resolves to an actively running instance of PostgreSQL (or compatible DB like AWS Redshift)

## Deployment:

On a system with `kubectl` and `helm` installed and configured for your running K8s cluster:

1. Run with default values in [values.yaml](values.yaml): `helm upgrade -i -n <HELM NAMESPACE> <NAME FOR THIS DEPLOYMENT> /path/to/this/helm/directory`
1. To override values, add the `--set PARAM=VALUE` parameter for each value.
  * eg: `--set env.DB_HOST=myPostgres.cluster.local --set env.DB_USER=myPostgres ...`  


## Special Considerations

**There is a cost optimization for AWS EKS clusters.**

Namespaces ending in "-qa" will be placed onto [SPOT](https://aws.amazon.com/ec2/spot/) nodes. It is highly recommended to utilize SPOT nodes for [AWS EKS](https://aws.amazon.com/eks/) (hosted Kubernetes cluster) to minimize cost. SPOT instances are highly discounted, but the tradeoff is that AWS can reclaim/terminate the machines if capacity is low, giving them to on-demand users. Doing such for non-production namespaces are a great cost savings measure, as non-production is more tolerant to partial downtime that results from nodes cycling in and out. Choosing multiple instance types in multiple Availability Zones for your EKS SPOT nodes would ensure there's adequate overall capacity to serve your cluster.

Tip: t3 vs t3a families are effectively identical in the big picture, but draws from vastly different pools of available machines.

**The deployed MediaThread service is not exposed.**

This is intentional, as the Django stack should not be directly accessible over web. A separate front end will be needed, whether Nginx or Apache.
