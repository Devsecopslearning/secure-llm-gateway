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
                script {
                    if (isUnix()) {
                        sh 'python -m venv $VENV_PATH'
                        sh '. $VENV_PATH/bin/activate && python -m pip install --upgrade pip'
                        sh '. $VENV_PATH/bin/activate && python -m pip install -r requirements.txt'
                    } else {
                        bat "python -m venv %VENV_PATH%"
                        bat "call %VENV_PATH%\\Scripts\\activate.bat && python -m pip install --upgrade pip"
                        bat "call %VENV_PATH%\\Scripts\\activate.bat && python -m pip install -r requirements.txt"
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh '. $VENV_PATH/bin/activate && python run_tests.py'
                    } else {
                        bat "call %VENV_PATH%\\Scripts\\activate.bat && python run_tests.py"
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    if (isUnix()) {
                        sh '. $VENV_PATH/bin/activate && python -m py_compile app/*.py'
                    } else {
                        bat "call %VENV_PATH%\\Scripts\\activate.bat && python -m py_compile app\\*.py"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
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
