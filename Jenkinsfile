pipeline {
    agent any

    environment {
        GITHUB_REPO = "https://github.com/yvesp78/Jenkins_devops_exams.git"
        APP_DIR = "app"
        DOCKER_USER = "monuser"
        IMAGE_NAME = "examen-app"
        IMAGE_TAG = "1.0.0"
        HELM_CHART_DIR = "helm-chart"
        JENKINS_USER = "jenkins"
        SERVICE_NAME = "web" // Nom exact du service dans docker-compose.yml
        API_URL = "http://63.35.53.134:8085/api/v1/movies/docs"
        NAMESPACES = "dev qa staging prod"
    }

    stages {
        stage('Cleanup Docker Containers') {
            steps {
                sh """
                echo "=== Arrêt et suppression de tous les conteneurs Docker existants ==="
                CONTAINERS=\$(docker ps -aq)
                if [ ! -z "\$CONTAINERS" ]; then
                    echo "⚠️ Conteneurs détectés, arrêt en cours..."
                    docker stop \$CONTAINERS
                    echo "Suppression des conteneurs..."
                    docker rm \$CONTAINERS
                    echo "✅ Tous les conteneurs arrêtés et supprimés"
                else
                    echo "✅ Aucun conteneur à arrêter"
                fi
                """
            }
        }

        stage('Checkout') {
            steps {
                git branch: 'main', url: "${GITHUB_REPO}"
            }
        }

        stage('Setup Environment') {
            steps {
                sh """
                chmod +x ./setup_dev_env.sh
                ./setup_dev_env.sh
                """
            }
        }

        stage('Docker Compose Up') {
            steps {
                dir("${APP_DIR}") {
                    sh """
                    echo "=== Construction et démarrage des conteneurs via docker-compose ==="
                    docker compose up -d
                    """
                }
            }
        }

        stage('API Health Check') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    script {
                        def success = false
                        def retries = 24  // 24 x 5 sec = 2 minutes
                        while(retries > 0 && !success) {
                            def httpCode = sh(
                                script: "curl -s -o /dev/null -w '%{http_code}' ${API_URL}",
                                returnStdout: true
                            ).trim()
                            if (httpCode == "200") {
                                echo "✅ API répond avec HTTP 200"
                                success = true
                            } else {
                                echo "⚠️ API non disponible encore, attente 5s..."
                                sleep 5
                                retries--
                            }
                        }
                        if (!success) {
                            error("❌ API ne répond pas après 2 minutes")
                        }
                    }
                }
            }
        }

        stage('Verify Pods') {
            steps {
                sh "k3s kubectl get pods -n dev"
            }
        }

        stage('API Tests') {
            steps {
                sh """
                echo "=== Installation des dépendances Python ==="
                python3 -m pip install --upgrade pip
                pip3 install -r requirements.txt

                echo "=== Lancement des tests API ==="
                python3 api_test.py
                """
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
