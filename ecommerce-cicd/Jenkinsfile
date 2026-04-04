pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME  = 'tushar327'         // Replace this
        APP_NAME            = 'ecommerce-app'
        IMAGE_NAME          = "${DOCKERHUB_USERNAME}/${APP_NAME}"
        IMAGE_TAG           = "${BUILD_NUMBER}"
        DOCKERHUB_CREDS     = credentials('dockerhub-creds')    // Add this in Jenkins credentials
    }

    triggers {
        githubPush()    // Triggers automatically on every GitHub push via webhook
    }

    stages {

        stage('Checkout') {
            steps {
                echo '--- Cloning code from GitHub ---'
                git branch: 'main',
                    url: 'https://github.com/YOUR_GITHUB_USERNAME/ecommerce-cicd.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "--- Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG} ---"
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ./app
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '--- Pushing image to Docker Hub ---'
                sh 'echo $DOCKERHUB_CREDS_PSW | docker login -u $DOCKERHUB_CREDS_USR --password-stdin'
                sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker push ${IMAGE_NAME}:latest"
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo '--- Deploying to Kubernetes ---'
                sh 'kubectl apply -f k8s/app/deployment.yaml'
                sh 'kubectl apply -f k8s/app/ingress.yaml'
                sh 'kubectl apply -f k8s/app/hpa.yaml'

                // Update image tag to force rolling update
                sh "kubectl set image deployment/ecommerce-deployment ecommerce=${IMAGE_NAME}:${IMAGE_TAG}"

                // Wait for rollout to complete
                sh 'kubectl rollout status deployment/ecommerce-deployment --timeout=120s'
            }
        }

        stage('Deploy Monitoring') {
            steps {
                echo '--- Deploying Prometheus and Grafana ---'
                sh 'kubectl apply -f k8s/monitoring/prometheus.yaml'
                sh 'kubectl apply -f k8s/monitoring/grafana.yaml'
            }
        }

        stage('Verify') {
            steps {
                echo '--- Verifying deployment ---'
                sh 'kubectl get pods -o wide'
                sh 'kubectl get services'
                sh 'kubectl get hpa'
                sh 'kubectl get ingress'
            }
        }
    }

    post {
        success {
            echo """
            ========================================
            Deployment SUCCESSFUL!
            Image: ${IMAGE_NAME}:${IMAGE_TAG}
            App: http://ecommerce.local
            ========================================
            """
        }
        failure {
            echo 'Pipeline FAILED. Rolling back...'
            sh 'kubectl rollout undo deployment/ecommerce-deployment'
        }
        always {
            sh 'docker logout'
            sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true"
        }
    }
}
