pipeline {
    agent any

    environment {
        VENV_PATH = '.venv'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh 'python -m venv $VENV_PATH'
                sh '. $VENV_PATH/bin/activate && python -m pip install --upgrade pip'
                sh '. $VENV_PATH/bin/activate && python -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh '. $VENV_PATH/bin/activate && python run_tests.py'
            }
        }

        stage('Build') {
            steps {
                sh '. $VENV_PATH/bin/activate && python -m py_compile app/*.py'
            }
        }

        stage('Deploy') {
            steps {
                // Customize deployment steps (copy, restart service, docker, etc.)
                echo 'Deploy step placeholder - update for your environment'
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed.'
        }
        failure {
            echo 'Build failed!'
        }
    }
}
