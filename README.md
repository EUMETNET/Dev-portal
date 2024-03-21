# Dev-portal Helm chart

# Install:
```sh
# Add repository
helm repo add rodeo https://rodeo-project.eu/Dev-portal/
helm repo update

# Install chart
helm install [RELEASE_NAME] rodeo/dev-portal -namespace dev-portal --create-namespace
```

# Uninstall:
```sh
helm delete [RELEASE_NAME] --namespace dev-portal
```

For the raw Helm repo index, see:
[index.yaml](index.yaml)
