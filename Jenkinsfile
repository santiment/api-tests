@Library('podTemplateLib')

import net.santiment.utils.podTemplates

slaveTemplates = new podTemplates()

slaveTemplates.dockerTemplate { label ->
  node(label) {
    container('docker') {
      withCredentials([
        string(credentialsId: 'discord_webhook', variable: 'DISCORD_WEBHOOK'),
        string(credentialsId: 'sanbase_api_key', variable: 'API_KEY')
      ]) {

        def scmVars = checkout scm
        def imageName = "api-tests"

        stage('Run tests') {
          RUN_STATUS = sh(script: "./bin/test.sh", returnStatus: true)

          if (RUN_STATUS != 0) {
            discordSend (
              description: 'API tests build failed.',
              footer: '',
              image: '',
              link: 'https://jenkins.internal.santiment.net/job/Santiment/job/api-tests/job/master/',
              result: 'FAILURE',
              thumbnail: '',
              title: 'Click here for details',
              webhookURL: DISCORD_WEBHOOK
            )
            currentBuild.result = 'FAILURE'
          }
        }
      }

      stage('Build image') {
        withCredentials([string(credentialsId: 'aws_account_id', variable: 'aws_account_id')]) {
          def awsRegistry = "${env.aws_account_id}.dkr.ecr.eu-central-1.amazonaws.com"

          docker.withRegistry("https://${awsRegistry}", "ecr:eu-central-1:ecr-credentials") {
            sh "docker build \
              -t ${awsRegistry}/${imageName}:${env.BRANCH_NAME} \
              -t ${awsRegistry}/${imageName}:${scmVars.GIT_COMMIT} \
              -f docker/Dockerfile ."
            sh "docker push ${awsRegistry}/${imageName}:${env.BRANCH_NAME}"
            sh "docker push ${awsRegistry}/${imageName}:${scmVars.GIT_COMMIT}"
          }
        }
      }
    }
  }
}
