# Automated CI/CD Pipeline with Monitoring for an E-Commerce App

A Python Flask e-commerce app deployed on Kubernetes (Minikube) with a full automated CI/CD pipeline using Jenkins + GitHub Webhooks, and real-time monitoring using Prometheus + Grafana.

---

## Project Structure

```
ecommerce-cicd/
├── app/
│   ├── app.py                  # Flask e-commerce app (with Prometheus metrics)
│   ├── Dockerfile              # Container image definition
│   ├── requirements.txt
│   └── templates/
│       ├── index.html          # Home page
│       └── products.html       # Products page
├── k8s/
│   ├── app/
│   │   ├── deployment.yaml     # Deployment + Service (2 replicas, rolling update)
│   │   ├── ingress.yaml        # NGINX Ingress
│   │   └── hpa.yaml            # Horizontal Pod Autoscaler
│   └── monitoring/
│       ├── prometheus.yaml     # Prometheus + AlertRules + RBAC
│       └── grafana.yaml        # Grafana
├── Jenkinsfile                 # Full CI/CD pipeline definition
└── README.md
```

---

## What This Project Does

| Feature | Detail |
|---|---|
| App | Flask e-commerce app with products, orders, /metrics endpoint |
| CI/CD | Jenkins pipeline triggered by GitHub webhook on every push |
| Build | Docker image built and pushed to Docker Hub automatically |
| Deploy | `kubectl apply` + rolling update — zero downtime |
| Autoscaling | HPA scales pods when CPU > 70% |
| Monitoring | Prometheus scrapes `/metrics` from pods every 15s |
| Dashboards | Grafana shows CPU, memory, request count, latency |
| Alerting | Prometheus alerts on pod down, high CPU, high latency |

---

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Hub account](https://hub.docker.com/)
- Jenkins (local or server)

---

## Step 1 — Replace YOUR_DOCKERHUB_USERNAME

In the files below, replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username:

- `k8s/app/deployment.yaml` — line with `image:`
- `Jenkinsfile` — line 4

Also replace `YOUR_GITHUB_USERNAME` in `Jenkinsfile` line 17.

---

## Step 2 — Start Minikube

```bash
minikube start
minikube addons enable ingress
minikube addons enable metrics-server
```

---

## Step 3 — Build and Push Docker Image Manually (First Time)

```bash
cd app

docker build -t YOUR_DOCKERHUB_USERNAME/ecommerce-app:latest .
docker login
docker push YOUR_DOCKERHUB_USERNAME/ecommerce-app:latest
```

---

## Step 4 — Deploy App to Kubernetes

```bash
kubectl apply -f k8s/app/deployment.yaml
kubectl apply -f k8s/app/ingress.yaml
kubectl apply -f k8s/app/hpa.yaml
```

---

## Step 5 — Deploy Monitoring

```bash
kubectl apply -f k8s/monitoring/prometheus.yaml
kubectl apply -f k8s/monitoring/grafana.yaml
```

---

## Step 6 — Check Everything is Running

```bash
kubectl get pods
kubectl get services
kubectl get hpa
kubectl get ingress
```

---

## Step 7 — Access the App

```bash
# Add to /etc/hosts
echo "$(minikube ip) ecommerce.local" | sudo tee -a /etc/hosts

# Or use this to open directly
minikube service ecommerce-service
```

Open browser: http://ecommerce.local

---

## Step 8 — Access Monitoring

```bash
# Prometheus
minikube service prometheus-service -n monitoring

# Grafana (login: admin / admin123)
minikube service grafana-service -n monitoring
```

### Setup Grafana Dashboard:
1. Login to Grafana → Configuration → Data Sources
2. Add Prometheus → URL: `http://prometheus-service.monitoring.svc.cluster.local:9090`
3. Save and Test
4. Dashboards → Import → Enter ID `3662` → Load (Kubernetes pod dashboard)
5. Import ID `11074` for custom app metrics

---

## Step 9 — Set Up Jenkins CI/CD

### In Jenkins:
1. New Item → Pipeline → Name: `ecommerce-cicd`
2. Pipeline → Definition: Pipeline script from SCM
3. SCM: Git → URL: your GitHub repo URL
4. Script Path: `Jenkinsfile`
5. Add Docker Hub credentials:
   - Manage Jenkins → Credentials → Global → Add Credentials
   - Kind: Username with password
   - ID: `dockerhub-creds`
   - Username: your Docker Hub username
   - Password: your Docker Hub password

### Set Up GitHub Webhook:
1. Go to your GitHub repo → Settings → Webhooks → Add webhook
2. Payload URL: `http://YOUR_JENKINS_IP:8080/github-webhook/`
3. Content type: `application/json`
4. Which events: Just the push event
5. Click Add webhook

Now every `git push` automatically triggers the full pipeline!

---

## App Endpoints

| Endpoint | Description |
|---|---|
| `/` | Home page with featured products |
| `/products` | All products with category filter |
| `/api/products` | Products JSON API |
| `/api/order` | POST — place an order |
| `/api/orders` | GET — view all orders |
| `/health` | Health check (used by K8s probes) |
| `/metrics` | Prometheus metrics (scraped every 15s) |

---

## Useful Commands

```bash
# Watch pods in real time
kubectl get pods -w

# View app logs
kubectl logs -f deployment/ecommerce-deployment

# Manual scale
kubectl scale deployment ecommerce-deployment --replicas=3

# Rollback
kubectl rollout undo deployment/ecommerce-deployment

# Check HPA activity
kubectl describe hpa ecommerce-hpa

# Get inside a pod
kubectl exec -it deployment/ecommerce-deployment -- /bin/bash
```

---

## Key Metrics Tracked by Prometheus

| Metric | What It Measures |
|---|---|
| `app_request_count_total` | Total requests per endpoint |
| `app_request_latency_seconds` | Response time per endpoint |
| `app_orders_total` | Total orders placed |
| `process_cpu_seconds_total` | CPU usage |
| `process_resident_memory_bytes` | Memory usage |
