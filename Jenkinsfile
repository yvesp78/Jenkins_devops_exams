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

        stage('Docker Compose Build & Verify API') {
            steps {
                dir("${APP_DIR}") {
                    sh """
                    echo "=== Construction et démarrage des conteneurs via docker-compose ==="
                    docker compose up -d

                    echo "=== Vérification que l'API répond avec HTTP 200 ==="
                    RETRIES=10
                    until [ \$RETRIES -eq 0 ]; do
                        HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8085)
                        if [ "\$HTTP_CODE" -eq 200 ]; then
                            echo "✅ API répond avec HTTP 200"
                            break
                        fi
                        echo "⚠️ API non disponible encore, attente..."
                        sleep 5
                        RETRIES=\$((RETRIES-1))
                    done

                    if [ "\$HTTP_CODE" -ne 200 ]; then
                        echo "❌ API ne répond pas après plusieurs tentatives"
                        exit 1
                    fi
                    """
                }
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
