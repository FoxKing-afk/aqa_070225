pipeline {
    agent any

    stages {
        stage('Clone source') {
            steps {
                git url: 'https://github.com/alex-pancho/aqa_070225', branch: 'main'
            }
        }
        stage('Build and activate venv') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Tests') {
            steps {
                sh '''
                . venv/bin/activate
                pytest -s -v "$WORKSPACE/lesson_24/test_lesson_24.py" --junitxml=$WORKSPACE/report.xml
                '''
                junit '**/report.xml'
            }
        }
    }
}