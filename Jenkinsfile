#!groovy

//loading https://code.sbb.ch/projects/KD_WZU/repos/wzu-pipeline-helper
@Library('wzu-pipeline-helper') _

pipeline {
    agent { label 'java' }
    tools {
        maven 'Apache Maven 3.3'
        jdk 'Oracle JDK 1.8 64-Bit'
    }
    stages {
         stage('Install & Unit Tests'){
             steps {
                timeout(time: 5, unit: 'MINUTES') {
                        sh """
                        pip install --user virtualenv
                        $HOME/.local/bin/virtualenv ENV
                        source ENV/bin/activate
                        pip install -r requirements.txt -U
                        nose2 --plugin nose2.plugins.junitxml --junit-xml
                        """
                }
            }
        }

        stage('When on develop, do nothing') {
            when {
                branch 'develop'
            }
            steps {
                sh 'ls'
            }
        }

        stage('When on master, Release: Adapt poms, tag, deploy and push.') {
            when {
                branch 'master'
            }
            steps {
                releaseMvn()
            }
        }
    }

        post {
        always {
            junit '*.xml'
        }
    }

}