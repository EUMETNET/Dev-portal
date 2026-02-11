# Configuring APISIX Routes with the API Management Tool

This guide explains how to use the [API Management Tool POC](https://github.com/EUMETNET/api-management-tool-poc) to configure APISIX routes for the Dev Portal.

## Prerequisites

- Node.js (>= 18.x)
- npm (>= 9.x)
- Dev Portal external services running (`./manage-services.sh up dev`)

Note: The manage-services script creates dummy routes (`/foo` and `/bar`) for testing.

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

### 3. Create Route Configuration

Create a YAML file in `configs/routes/` for your local development routes:

```bash
# Create the configuration file
touch configs/routes/dev-test.yaml
```

**Example:** `configs/routes/dev-test.yaml`

```yaml
id: dev-test
version: 1.0.0
platforms: 
  - LOCAL-DEV
routes:
  - route:
      disableResponseRewrite: true  # Disable custom plugin not installed by default
      id: baz
      endpoint: http://web1:80/
      ratelimitAuth:
        requestRate:
          rate: 10
          burst: 20
        quota:
          count: 100
          time_window: 60
      ratelimitAnon:
        requestRate:
          rate: 2
          burst: 5
        quota:
          count: 30
          time_window: 60
      cors: true
      overwrite:
        upstream:
          scheme: http             # Force HTTP (default is HTTPS)
          nodes:
            "web1:80": 1           # Specify backend and port
            
  - route:
      disableResponseRewrite: true
      id: qux
      endpoint: http://web2:80/
      ratelimitAuth:
        requestRate:
          rate: 10
          burst: 20
        quota:
          count: 100
          time_window: 60
      ratelimitAnon:
        requestRate:
          rate: 2
          burst: 5
        quota:
          count: 30
          time_window: 60
      cors: true
      overwrite:
        upstream:
          scheme: http
          nodes:
            "web2:80": 1
```

**Configuration notes:**
- `disableResponseRewrite: true` - Disables the `dynamic-response-rewrite` plugin (not installed by default in APISIX)
- `endpoint` - Must include the port (e.g., `http://web1:80/`)
- `overwrite.upstream.scheme` - Forces HTTP scheme (tool defaults to HTTPS)
- `overwrite.upstream.nodes` - Specifies backend servers and ports

### 4. Create Deployment Script

Create a script to deploy routes to both APISIX instances:

```bash
# In the api-management-tool-poc directory
touch deploy-routes.sh
chmod +x deploy-routes.sh
```

**deploy-routes.sh:**
```bash
#!/bin/bash

set -e

echo "Deploying routes to both APISIX instances..."

# Deploy to local APISIX Instance 1
echo ""
echo "Deploying to Instance 1 (ports 9080/9180)..."
export PLATFORM=LOCAL-DEV
export BASE_URL=http://127.0.0.1:9080
export ADMIN_API_URL=http://127.0.0.1:9180
export APISIX_API_KEY=edd1c9f034335f136f87ad84b625c8f1

npm run dev

# Deploy to local APISIX Instance 2
echo ""
echo "Deploying to Instance 2 (ports 9181/9280)..."
export BASE_URL=http://127.0.0.1:9181
export ADMIN_API_URL=http://127.0.0.1:9280

npm run dev

echo ""
echo "Both instances configured successfully!"
echo ""
echo "Verify routes at: http://localhost:3002/routes"
```

### 5. Deploy Routes

Note: The tool removes dummy routes (`/foo` and `/bar`). 

Run the deployment script:

```bash
./deploy-routes.sh
```

**Expected output:**
```
Deploying routes to both APISIX instances...

Deploying to Instance 1 (ports 9080/9180)...
Routes: 4, Upstreams: 2

Deploying to Instance 2 (ports 9181/9280)...
Routes: 4, Upstreams: 2

Both instances configured successfully!

Verify routes at: http://localhost:3002/routes
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