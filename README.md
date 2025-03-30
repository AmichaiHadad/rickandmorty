# Rick and Morty API

A REST API for retrieving Rick and Morty characters that are Human, Alive, and from Earth (including variants).

## Quick Install with Helm (Recommended)

### Prerequisites
- Kubernetes cluster (minikube or kind for local development)
- Helm v3
- Docker

### Installation Steps

1. Clone the repository and navigate to the project directory

2. Build and load the Docker image:
```bash
# Build image
docker build -t rick-and-morty-api:latest .

# Load image to your cluster
# For minikube:
minikube image load rick-and-morty-api:latest
# For kind:
kind load docker-image rick-and-morty-api:latest
```

3. Install ingress controller (if needed):
```bash
# For minikube:
minikube addons enable ingress
# For kind:
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/kind/deploy.yaml
```

4. Deploy with Helm:
```bash
helm install rick-and-morty-api ./helm/rick-and-morty
```

5. Add host entry (for local development):
```
127.0.0.1 rickandmorty.local
```

6. Access the API:
   - With ingress: http://rickandmorty.local
   - With port forwarding: 
     ```bash
     kubectl port-forward svc/rick-and-morty-api 8080:80
     # Then access http://localhost:8080
     ```

## Alternative Installation Methods

### Docker Only

```bash
# Build and run
docker build -t rick-and-morty-api .
docker run -p 5000:5000 rick-and-morty-api

# Access at http://localhost:5000
```

### Kubernetes (without Helm)

```bash
# Build and load image (see step 2 above)
# Install ingress (see step 3 above)

# Apply manifests
kubectl apply -f yamls/deployment.yaml
kubectl apply -f yamls/service.yaml
kubectl apply -f yamls/ingress.yaml

# Access as described in step 6 above
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Access at http://localhost:5000
```

## Customize Installation

### Helm Values

```bash
# Override specific values
helm install rick-and-morty-api ./helm/rick-and-morty --set replicaCount=3

# Using custom values file
helm install rick-and-morty-api ./helm/rick-and-morty -f custom-values.yaml
```

Example `custom-values.yaml`:
```yaml
replicaCount: 3
image:
  repository: my-registry/rick-and-morty-api
  tag: v1.0.0
ingress:
  hosts:
    - host: rick-api.example.com
      paths:
        - path: /
          pathType: Prefix
```

## Management Commands

```bash
# Check deployment status
helm status rick-and-morty-api
kubectl get pods,svc,ingress -l app=rick-and-morty-api

# Upgrade
helm upgrade rick-and-morty-api ./helm/rick-and-morty

# Uninstall
helm uninstall rick-and-morty-api
```

## CI/CD with GitHub Actions

This project includes a GitHub Actions workflow for continuous integration and testing.

### Workflow Overview

The workflow automatically:
1. Sets up a Kubernetes cluster in the GitHub Actions runner
2. Builds and deploys the application
3. Runs automated tests on all API endpoints
4. Reports the test results

### Workflow Steps

1. **Build Docker Image**: Creates the application container image
2. **Create Kind Cluster**: Spins up a local Kubernetes cluster with Kind
3. **Install NGINX Ingress**: Sets up the ingress controller
4. **Deploy with Helm**: Installs the application using our Helm chart
5. **Run Tests**: Executes Python tests against all API endpoints
   - `/healthcheck`: Verifies the API service is running
   - `/`: Checks the API information endpoint
   - `/characters`: Validates character data response

### Running the Workflow

The workflow runs automatically on:
- Push to the main branch
- Pull requests to the main branch

You can also trigger it manually from the Actions tab in GitHub.

### Workflow File

The workflow configuration is located at `.github/workflows/k8s-test.yml`.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/characters` | GET | All characters matching criteria (Human, Alive, from Earth) |
| `/healthcheck` | GET | Service health status |

## Project Structure

```
├── app.py                    # Flask application with API endpoints
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── rick_and_morty_characters.csv  # Cached character data
├── yamls/                    # Kubernetes manifests
└── helm/                     # Helm chart
    └── rick-and-morty/       # Chart for the application
└── .github/                  # GitHub configuration
    └── workflows/            # GitHub Actions workflows
        └── k8s-test.yml      # K8s test workflow
``` 