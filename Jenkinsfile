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
            parallel {
                stage('Start Docker Compose') {
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
                                def retries = 24  // 24 x 5sec = 2 minutes
                                while(retries > 0 && !success) {
                                    def httpCode = sh(
                                        script: 'curl -s -o /dev/null -w "%{http_code}" http://63.35.53.134:8085/api/v1/movies/docs',
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
