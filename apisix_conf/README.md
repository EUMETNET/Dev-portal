# Configuring APISIX Routes with the API Management Tool

This guide explains how to use the [API Management Tool POC](https://github.com/EUMETNET/api-management-tool-poc) to configure APISIX routes for Dev Portal instead of the [setup.sh](setup.sh) script.

Note: When running the command `./manage-services.sh up dev`, it will also run the `setup.sh` script by default, which creates dummy routes (`/foo` and `/bar`) for testing purposes.

## Prerequisites for the API Management Tool

- Node.js (>= 18.x)
- npm (>= 9.x)
- Dev Portal external services running (`./manage-services.sh up dev`)

## Setup

### 1. Clone the API Management Tool

Clone the repository to **your workspace**:

```bash
# Navigate to your workspace root
cd /path/to/your/workspace

# Clone the API management tool
git clone git@github.com:EUMETNET/api-management-tool-poc.git
cd api-management-tool-poc
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Create Apisix Configuration

The API Management Tool uses YAML files in the `configs/` directory:
- **Routes**: `configs/routes/` - Define API endpoints and upstream services
- **Consumer groups**: `configs/groups/` - Define user groups and rate limits

**Example of a consumer group** (`configs/groups/eumetnet.yaml`):
```yaml
id: EumetnetUser
ratelimit:
  quota:
    count: 500
    time_window: 60
```

This creates a consumer group with higher rate limits for EUMETNET users (500 req/min).

Create a route configuration file:

```bash
touch configs/routes/dev-test.yaml
```

**Example of route configuration** (`configs/routes/dev-test.yaml`);

```yaml
id: dev-test
version: 1.0.0
platforms: 
  - LOCAL-DEV
routes:
  - route:
      disableResponseRewrite: true
      id: baz
      endpoint: http://web1:80/
      ratelimitAuth:
        requestRate:
          rate: 10
          burst: 20
        quota:
          count: 10
          time_window: 60
      ratelimitAnon:
        requestRate:
          rate: 1
          burst: 5
        quota:
          count: 10
          time_window: 60
      cors: true
      overwrite:
        upstream:
          scheme: http
          nodes:
            "web1:80": 1
            
  - route:
      disableResponseRewrite: true
      id: qux
      endpoint: http://web2:80/
      ratelimitAuth:
        requestRate:
          rate: 100
          burst: 200
        quota:
          count: 200
          time_window: 60
      ratelimitAnon:
        requestRate:
          rate: 10
          burst: 20
        quota:
          count: 100
          time_window: 60
      cors: true
      overwrite:
        upstream:
          scheme: http
          nodes:
            "web2:80": 1
```

This creates two routes (`/baz` and `/qux`) with both authenticated and anonymous access (four routes in total).

Route `/baz`: Authenticated users get 10 requests/second (burst 20) and 10 requests/minute quota, while anonymous users have stricter rate limits of 1 request/second (burst 5) and 10 requests/minute quota.

Route `/qux`: Authenticated users get 100 requests/second (burst 200) and 200 requests/minute quota, while anonymous users have stricter rate limits of 10 request/second (burst 20) and 100 requests/minute quota.

Consumer Group Limits: Users in the EumetnetUser consumer group would have an additional group-level limit of 500 requests/minute quota that applies across all routes. Regular User group members only have the route-level limits shown above. Anonymous users (no API key) are limited per IP address and have the lowest rate limits.

The routes proxy to HTTP backend servers web1 and web2. APISIX automatically selects the authenticated route when an API key is provided (via apikey header or query parameter), and falls back to the anonymous route when no API key is provided.


**Configuration notes:**
- `disableResponseRewrite: true` - Disables the `dynamic-response-rewrite` plugin (not installed by default in APISIX)
- `endpoint` - Must include the port (e.g., `http://web1:80/`)
- `overwrite.upstream.scheme` - Forces HTTP scheme (tool defaults to HTTPS)
- `overwrite.upstream.nodes` - Specifies backend servers and ports

### 4. Create Deployment Script

Create a script to deploy consumer groups and routes to both APISIX instances:

```bash
# In the api-management-tool-poc directory
touch deploy-routes.sh
chmod +x deploy-routes.sh
```

**deploy-routes.sh:**
```bash
#!/bin/bash
# Deploy routes to local APISIX instances
set -euo pipefail

deploy() {
    echo "Deploying to $3..."
    PLATFORM=LOCAL-DEV BASE_URL="$1" ADMIN_API_URL="$2" \
        APISIX_API_KEY=edd1c9f034335f136f87ad84b625c8f1 npm run dev
}

echo "Deploying routes..."
deploy "http://127.0.0.1:9080" "http://127.0.0.1:9180" "Instance 1"
deploy "http://127.0.0.1:9181" "http://127.0.0.1:9280" "Instance 2"

echo "Done! View routes at: http://localhost:3002/routes"
```

### 5. Deploy Routes

Note: The tool removes dummy routes (`/foo` and `/bar`). 

Run the deployment script:

```bash
./deploy-routes.sh
```

**Expected output:**
```
Deploying routes...
Deploying to Instance 1...
..
Routes: 4, Upstreams: 2
Deploying to Instance 2...
..
Routes: 4, Upstreams: 2
Done! View routes at: http://localhost:3002/routes
```

### 6. Verify Configuration

1. **Check APISIX directly:**
   ```bash
   curl -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
     http://localhost:9180/apisix/admin/routes | jq
   ```

2. **Check Dev Portal UI:**
   - Navigate to http://localhost:3002
   - View available routes

3. **Test route access:**
   ```bash
   # Get API key from the Dev Portal UI
   curl -H "apikey: YOUR_API_KEY" http://localhost:9080/baz
   # Expected: {"message": "Hello from dummy upstream server web1"}
   ```

## Modifying Existing Routes

To adapt routes from other environments:

### Add platform filter
```yaml
platforms: 
  - LOCAL-DEV  # Add this to deploy to local environment only
```

### Disable custom plugin
```yaml
disableResponseRewrite: true  # If dynamic-response-rewrite plugin not installed
```

### Remove production-specific settings
- Remove API key references
```
apikey:
  headerParam: 'Authorization'
  secretName: <SOME_API_KEY>
```

## References
- [API Management Tool POC Repository](https://github.com/EUMETNET/api-management-tool-poc)