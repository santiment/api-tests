properties([
  pipelineTriggers([cron('00 * * * *')]),
  disableConcurrentBuilds(),
  buildDiscarder(logRotator(numToKeepStr: '10'))
])
podTemplate(label: 'api-tests', containers: [
  containerTemplate(name: 'docker', image: 'docker', ttyEnabled: true, command: 'cat', envVars: [
    envVar(key: 'DOCKER_HOST', value: 'tcp://docker-host-docker-host:2375')
  ]),
  containerTemplate(name: 'api-tests', image: '913750763724.dkr.ecr.eu-central-1.amazonaws.com/api-tests:master', ttyEnabled: true, command: 'cat', envVars: [
    envVar(key: 'TOP_PROJECTS_BY_MARKETCAP', value: '100')
  ])
]) {
  node('api-tests') {
    stage('Run Build') {
      container('docker') {
        def scmVars = checkout scm

        withCredentials([
          string(
            credentialsId: 'aws_account_id',
            variable: 'aws_account_id'
          )
        ]) {
          def awsRegistry = "${env.aws_account_id}.dkr.ecr.eu-central-1.amazonaws.com"
          docker.withRegistry("https://${awsRegistry}", "ecr:eu-central-1:ecr-credentials") {
            sh "docker build -t ${awsRegistry}/api-tests:${env.BRANCH_NAME} -t ${awsRegistry}/api-tests:${scmVars.GIT_COMMIT} ."
            sh "docker push ${awsRegistry}/api-tests:${env.BRANCH_NAME}"
            sh "docker push ${awsRegistry}/api-tests:${scmVars.GIT_COMMIT}"
          }
        }
      }
      container('api-tests') {
      withCredentials([
        string(
          credentialsId: 'discord_webhook',
          variable: 'DISCORD_WEBHOOK'
        ),
        string(
          credentialsId: 'sanbase_api_key',
          variable: 'API_KEY'
        ),
      ]) {
          sh "python api_tests.py --sanity"
          publishHTML (target: [
            allowMissing: false,
            alwaysLinkToLastBuild: false,
            keepAll: true,
            reportDir: 'output',
            reportFiles: 'index.html, output.json',
            reportName: "Test Report"
         ])
         discordSend (
           description: '${env.JOB_NAME} ended with status ${env.BUILD_STATUS}. Click the link to see details.',
           footer: '',
           image: '',
           link: '${env.BUILD_URL}',
           result: 'SUCCESS',
           thumbnail: '',
           title: '',
           webhookURL: '$discord_webhook'
         )
        }
      }
    }
  }
}
