pipeline {
    agent any

    environment {
        VENV = "${WORKSPACE}/.venv"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Version') {
            steps {
                sh '''
                python3 --version
                pip3 --version
                '''
            }
        }

        stage('Create Virtual Environment') {
            steps {
                sh '''
                python3 -m venv .venv
                . .venv/bin/activate
                pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                . .venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                . .venv/bin/activate

                if [ -d tests ]; then
                    pytest tests -v
                else
                    echo "No tests found"
                fi
                '''
            }
        }

        stage('Application Validation') {
            steps {
                sh '''
                . .venv/bin/activate

                python -m py_compile app.py
                python -m py_compile scanner.py
                python -m py_compile cli.py
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully'
        }

        failure {
            echo 'Pipeline failed'
        }

        always {
            cleanWs()
        }
    }
}
