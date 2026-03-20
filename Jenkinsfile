pipeline {
    agent any

    environment {
        AWS_REGION = 'eu-west-1'
        ECR_REPO = '159906127313.dkr.ecr.eu-west-1.amazonaws.com/secure-app-real'
    }

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t secure-app:latest .'
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                aquasec/trivy image --severity CRITICAL --exit-code 1 secure-app:latest
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                aws ecr get-login-password --region $AWS_REGION | docker login \
                --username AWS --password-stdin $ECR_REPO

                docker tag secure-app:latest $ECR_REPO:latest
                docker push $ECR_REPO:latest
                '''
            }
        }
    }
}