pipeline {
    agent any

    environment {
        GITHUB_REPO = "https://github.com/yvesp78/Jenkins_devops_exams.git"
        APP_DIR = "app"
        DOCKER_USER = "yvesp78"
        DOCKER_IMAGE = "examen-app"
        DOCKER_TAG = "1.0.0"
        HELM_CHART_DIR = "helm-chart"
        JENKINS_USER = "jenkins"
        SERVICE_NAME = "web" // Nom exact du service dans docker-compose.yml
        API_URL = "http://63.35.53.134:8085/api/v1/movies/docs"
        NAMESPACES = "dev qa staging prod"
    }

    stages {

        // ===================== BUILD =====================
        stage('build') {
            stages {
                stage('Cleanup Docker Containers') {
                    steps {
                        sh '''
                        echo "=== Arrêt et suppression de tous les conteneurs Docker existants ==="
                        CONTAINERS=$(docker ps -aq)
                        if [ ! -z "$CONTAINERS" ]; then
                            docker stop $CONTAINERS
                            docker rm $CONTAINERS
                            echo "✅ Tous les conteneurs arrêtés et supprimés"
                        else
                            echo "✅ Aucun conteneur à arrêter"
                        fi
                        '''
                    }
                }

                stage('Checkout') {
                    steps {
                        git branch: 'main', url: "${GITHUB_REPO}"
                    }
                }

                stage('Setup Environment') {
                    steps {
                        sh '''
                        chmod +x ./setup_dev_env.sh
                        ./setup_dev_env.sh
                        '''
                    }
                }

                stage('Docker Compose Up') {
                    steps {
                        dir("${APP_DIR}") {
                            sh '''
                            echo "=== Construction et démarrage des conteneurs via docker-compose ==="
                            docker compose up -d
                            '''
                        }
                    }
                }
            }
        }

        // ===================== TEST: INTEGRATION & QUALITY =====================
        stage('test: integration-&-quality') {
            stages {
                stage('API Health Check') {
                    steps {
                        timeout(time: 2, unit: 'MINUTES') {
                            script {
                                def success = false
                                def retries = 24
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
            }
        }

        // ===================== TEST: FUNCTIONAL =====================
        stage('test: functional') {
            stages {
                stage('API Tests') {
                    steps {
                        sh '''
                        echo "=== Installation des dépendances Python ==="
                        python3 -m pip install --upgrade pip
                        pip3 install -r requirements.txt

                        echo "=== Lancement des tests API ==="
                        python3 api_test.py
                        '''
                    }
                }
            }
        }

        // ===================== DOCKER PUSH =====================
        stage('Docker Push') {
            environment {
                DOCKER_PASS = credentials("DOCKER_HUB_PASS")
            }
            steps {
                script {
                    dir("${APP_DIR}") {
                        sh """
                        echo "=== Build des images via Docker Compose ==="
                        docker compose build

                        echo "=== Login DockerHub ==="
                        echo \$DOCKER_PASS | docker login -u ${DOCKER_USER} --password-stdin

                        echo "=== Retag & Push des images générées ==="
                        for IMAGE in \$(docker images --format '{{.Repository}}:{{.Tag}}' | grep 'jenkins_devops_exams_pipeline-'); do
                            SERVICE_NAME=\$(echo \$IMAGE | cut -d':' -f1 | sed 's/jenkins_devops_exams_pipeline-//')
                            echo "🔄 Retag \$IMAGE -> ${DOCKER_USER}/\${SERVICE_NAME}:${DOCKER_TAG}"
                            docker tag \$IMAGE ${DOCKER_USER}/\${SERVICE_NAME}:${DOCKER_TAG}
                            docker push ${DOCKER_USER}/\${SERVICE_NAME}:${DOCKER_TAG}
                        done
                        """
                    }
                }
            }
        }


        // ===================== DEPLOYMENT =====================
        stage('Deploiement en dev') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh '''
                    # === Définir l'architecture et découpage micro-services ici avant déploiement ===
                    rm -Rf .kube
                    mkdir .kube
                    cat $KUBECONFIG > .kube/config
                    cp charts/values.yaml values.yml
                    sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app ./charts --values=values.yml --namespace dev
                    '''
                }
            }
        }

        stage('Deploiement en staging') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh '''
                    rm -Rf .kube
                    mkdir .kube
                    cat $KUBECONFIG > .kube/config
                    cp charts/values.yaml values.yml
                    sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app ./charts --values=values.yml --namespace staging
                    '''
                }
            }
        }

        stage('Deploiement en prod') {
            when {
                branch 'main'
            }
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                input message: 'Voulez-vous déployer en production ?', ok: 'Oui'
                script {
                    sh '''
                    rm -Rf .kube
                    mkdir .kube
                    cat $KUBECONFIG > .kube/config
                    cp charts/values.yaml values.yml
                    sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app ./charts --values=values.yml --namespace prod
                    '''
                }
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
