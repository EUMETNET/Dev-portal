# Install the chart repository

```bash
helm repo add dev-portal http://rodeo-project.eu/Dev-portal/
helm repo update
```

# Testing the Chart
Execute the following for testing the chart:

```bash
helm install dev-portal dev-portal/dev-portal --dry-run --debug -n dev-portal --create-namespace --values=./values.yaml
```

# Installing the Chart
Execute the following for installing the chart:

```bash
helm install dev-portal dev-portal/dev-portal -n dev-portal --create-namespace --values=./values.yaml
```

# Deleting the Chart
Execute the following for deleting the chart:

```bash
## Delete the Helm Chart
helm delete -n dev-portal dev-portal
## Delete the Namespace
kubectl delete namespace dev-portal
```

# Chart Configuration
The following table lists the configurable parameters of the Smartmetserver chart and their default values.

*The parameters will be updating.*

| Parameter | Description | Default |
| - | - | - |
| `imageCredentials.enabled` | Does the image pulling need authentication | `true` |
| `imageCredentials.registry` | Registry where the image is pulled | `ghcr.io` |
| `imageCredentials.username` | Username for the image registry | `""` |
| `imageCredentials.password` | Password for the image registry | `smartmetserver` |
| `backend.name` | Backend deployment's name | `dev-portal-backend` |
| `backend.image.repository` | Repository for backend image | `eurodeo/dev-portal/backend` |
| `backend.image.pullPolicy` | Policy for backend image pulling | `IfNotPresent` |
| `backend.image.tag` | Tag for the backend image | `latest` |
| `backend.replicaCount` | Number of backend replicas | `2` |
| `backend.containerport` | Port for the backend container | `8082` |
| `backend.service.type` | Type of the backend service | `ClusterIP` |
| `backend.service.port` | Port for the backend service | `80` |
| `backend.config.log_level` | Log level for the backend | `INFO` |
| `backend.config.keycloak_cluster_url` | URL for the Keycloak service | `http://keycloak.keycloak.svc.cluster.local` |
| `backend.secrets.secretName` | Name of a existing secret for the backend. If empty, one is created| `""` |
| `backend.secrets.vault_url` | URL for the Vaul service | `http://vault.vault.svc.cluster.local:8200` |
| `backend.secrets.vault_token` | Token for the Vault | `""` |
| `backend.secrets.vault_path` | Path where the backend will store secrets | `apisix-dev/consumers` |
| `backend.secrets.apisix_keypath` | Path where secret's will be found in Apisix | `"$secret://vault/dev/"` |
| `backend.secrets.keycloak_client_id` | Client ID for Keycloak | `dev-portal-api` |
| `backend.secrets.keycloak_client_secret` | Client secret for Keycloak | `""` |
| `backend.readinessProbe.enabled` | Is readiness probe enabled | `true` |
| `backend.readinessProbe.initialDelaySeconds` | Initial delay for readiness probe | `2` |
| `backend.livenessProbe.enabled` | Is liveness probe enabled | `true` |
| `backend.livenessProbe.initialDelaySeconds` | Initial delay for liveness probe | `10` |
| `backend.livenessProbe.periodSeconds` | Period for liveness probe | `5` |
| `backend.autoscaling.enabled` | Is backend autoscaling enabled | `false` |
| `backend.autoscaling.minReplicas` | Minimum number of replicas for backend's autoscaling | `2` |
| `backend.autoscaling.maxReplicas` | Maximum number of replicas for backend's autoscaling | `100` |
| `backend.autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization percentage for autoscaling | `80` |
| `backend.autoscaling.targetMemoryUtilizationPercentage` | Target memory utilization percentage for autoscaling | `80` |
| `frontend.name` | Frontend deployment's name | `dev-portal-frontend` |
| `frontend.image.repository` | Repository for frontend image | `eurodeo/dev-portal/ui` |
| `frontend.image.pullPolicy` | Policy for frontend image pulling | `IfNotPresent` |
| `frontend.image.tag` | Tag for the frontend image | `latest` |
| `frontend.replicaCount` | Number of frontend replicas | `2` |
| `frontend.containerport` | Port for the frontend container | `443` |
| `frontend.service.type` | Type of the frontend service | `ClusterIP` |
| `frontend.service.port` | Port for the frontend service | `80` |
| `frontend.autoscaling.enabled` | Is frontend autoscaling enabled | `false` |
| `frontend.autoscaling.minReplicas` | Minimum number of replicas for frontend's autoscaling | `2` |
| `frontend.autoscaling.maxReplicas` | Maximum number of replicas for frontend's autoscaling | `100` |
| `frontend.autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization percentage for autoscaling | `80` |
| `frontend.autoscaling.targetMemoryUtilizationPercentage` | Target memory utilization percentage for autoscaling | `80` |
| `frontend.keycloak_url` | URL for Keycloak | `http://localhost:8080` |
| `frontend.keycloak_logout_url` | Logout URL for Keycloak | `http://localhost` |
| `keycloak_realm` | Realm for Keycloak | `test` |
| `ingress.enabled` | Is ingress enabled | `false` |
| `ingress.className` | Class name for ingress | `nginx` |
| `ingress.annotations` | Annotations for ingress | `{ certmanager.k8s.io/cluster-issuer: letsencrypt-prod, kubernetes.io/tls-acme: "true", external-dns.alpha.kubernetes.io/hostname: localhost, external-dns.alpha.kubernetes.io/target: 127.0.0.1 }` |
| `ingress.host` | Host for ingress | `localhost` |
| `ingress.tls` | TLS for ingress | `{ secretName: devportal-tls, hosts: [localhost] }` |
