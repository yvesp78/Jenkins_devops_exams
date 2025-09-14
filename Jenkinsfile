pipeline {
    agent any  // ou label 'docker-helm-agent' si tu as un agent spécifique

    environment {
        GITHUB_REPO = "https://github.com/yvesp78/Jenkins_devops_exams.git"
        APP_DIR = "app"
        DOCKER_USER = "monuser"
        IMAGE_NAME = "examen-app"
        IMAGE_TAG = "1.0.0"
        HELM_CHART_DIR = "helm-chart"
        JENKINS_USER = "jenkins"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: "${GITHUB_REPO}"
            }
        }

        stage('Setup Environment') {
            steps {
                // Rendre ton script exécutable et l'exécuter
                sh """
                chmod +x ./setup_dev_env.sh
                ./setup_dev_env.sh
                """
            }
        }

        stage('Docker Compose Build & Push') {
            steps {
                dir("${APP_DIR}") {
                    sh """
                    echo "=== Construction des images via docker-compose ==="
                    docker-compose build
                    """
                }
            }
        }

        stage('Deploy DEV with Helm') {
            steps {
                sh """
                echo "=== Déploiement sur namespace dev avec Helm ==="
                helm upgrade --install ${IMAGE_NAME} ${HELM_CHART_DIR} -n dev \
                  --set image.repository=${DOCKER_USER}/${IMAGE_NAME},image.tag=${IMAGE_TAG}
                """
            }
        }

        stage('Verify Pods') {
            steps {
                sh "k3s kubectl get pods -n dev"
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline terminé avec succès."
        }
        failure {
            echo "❌ Pipeline échoué !"
        }
    }
}
