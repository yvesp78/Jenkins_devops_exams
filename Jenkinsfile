pipeline {
    agent any

    environment {
        GITHUB_REPO   = "https://github.com/yvesp78/Jenkins_devops_exams.git"
        APP_DIR       = "."
        DOCKER_USER   = "yvesp78"
        DOCKER_IMAGE  = "examen-app"
        DOCKER_TAG    = "1.0.0"
        HELM_CHART    = "./charts"
        JENKINS_USER  = "jenkins"
        API_URL       = "http://63.35.53.134:8085/api/v1/movies/docs"
    }

    stages {
        stage('build: cleanup') {
            steps {
                sh '''
                echo "=== Arrêt et suppression de tous les conteneurs Docker existants ==="
                CONTAINERS=$(docker ps -aq)
                if [ ! -z "$CONTAINERS" ]; then
                    echo "⚠️ Conteneurs détectés, arrêt en cours..."
                    docker stop $CONTAINERS
                    docker rm $CONTAINERS
                    echo "✅ Tous les conteneurs arrêtés et supprimés"
                else
                    echo "✅ Aucun conteneur à arrêter"
                fi
                '''
            }
        }

        stage('build: checkout') {
            steps {
                git branch: 'main', url: "${GITHUB_REPO}"
            }
        }

        stage('build: setup-env') {
            steps {
                sh '''
                chmod +x ./setup_dev_env.sh
                ./setup_dev_env.sh
                '''
            }
        }

        stage('build: docker-compose') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                    echo "=== Build des images via Docker Compose ==="
                    docker compose build
                    '''
                }
            }
        }

        stage('build: docker-push') {
            environment {
                DOCKER_PASS = credentials("DOCKER_HUB_PASS")
            }
            steps {
                sh '''
                echo "=== Login DockerHub ==="
                echo $DOCKER_PASS | docker login -u ${DOCKER_USER} --password-stdin

                echo "=== Tag & Push des images ==="
                docker tag jenkins_devops_exams_pipeline-movie_service ${DOCKER_USER}/${DOCKER_IMAGE}-movie:${DOCKER_TAG}
                docker tag jenkins_devops_exams_pipeline-cast_service ${DOCKER_USER}/${DOCKER_IMAGE}-cast:${DOCKER_TAG}

                docker push ${DOCKER_USER}/${DOCKER_IMAGE}-movie:${DOCKER_TAG}
                docker push ${DOCKER_USER}/${DOCKER_IMAGE}-cast:${DOCKER_TAG}
                '''
            }
        }

        stage('test: api-health') {
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
                                echo "⚠️ API non dispo encore, attente 5s..."
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

        stage('test: api-functional') {
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

        stage('deploy: dev') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                sh '''
                echo "=== Déploiement DEV avec Helm ==="
                rm -Rf .kube
                mkdir .kube
                cat $KUBECONFIG > .kube/config

                cp charts/values.yaml values.yml
                sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" values.yml

                helm upgrade --install app ${HELM_CHART} --values=values.yml --namespace dev
                '''
            }
        }

        stage('deploy: staging') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                sh '''
                echo "=== Déploiement STAGING avec Helm ==="
                rm -Rf .kube
                mkdir .kube
                cat $KUBECONFIG > .kube/config

                cp charts/values.yaml values.yml
                sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" values.yml

                helm upgrade --install app ${HELM_CHART} --values=values.yml --namespace staging
                '''
            }
        }

        stage('deploy: prod') {
            when {
                branch "master"
            }
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                timeout(time: 15, unit: "MINUTES") {
                    input message: '🚀 Déployer en production ?', ok: 'Yes'
                }
                sh '''
                echo "=== Déploiement PROD avec Helm ==="
                rm -Rf .kube
                mkdir .kube
                cat $KUBECONFIG > .kube/config

                cp charts/values.yaml values.yml
                sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" values.yml

                helm upgrade --install app ${HELM_CHART} --values=values.yml --namespace prod
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline terminé avec succès."
        }
        failure {
            echo "❌ Pipeline échoué."
        }
    }
}
