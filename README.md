# Dev-portal Helm chart

# Install:
```sh
# Add repository
helm repo add meteogate https://eumetnet.github.io/Dev-portal/
helm repo update

# Install chart
helm install [RELEASE_NAME] meteogate/dev-portal --namespace dev-portal --create-namespace
```

# Uninstall:
```sh
helm delete [RELEASE_NAME] --namespace dev-portal
```

# Repo Index
For the raw Helm repo index, see:
[index.yaml](index.yaml)
