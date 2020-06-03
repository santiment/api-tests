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
        [
          $class: 'AmazonWebServicesCredentialsBinding', 
          accessKeyVariable: 'AWS_ACCESS_KEY_ID', 
          credentialsId: 's3_api-tests-json', 
          secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
        ]
      ]) {
          sh "apt-get install -y curl unzip"
          sh 'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"'
          sh "unzip awscliv2.zip"
          sh "./aws/install"
          RUN_STATUS = sh (
            script: "python api_tests.py --sanity",
            returnStatus: true
          )
          publishHTML (target: [
            allowMissing: false,
            alwaysLinkToLastBuild: false,
            keepAll: true,
            reportDir: 'output',
            reportFiles: 'index.html, output.json',
            reportName: "Test Report"
          ]) 
          sh "aws s3 cp output/output.json s3://api-tests-json/latest_report.json --acl public-read"
          sh "aws s3 cp output/output.json s3://api-tests-json/output-${BUILD_NUMBER}.json --acl public-read"
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
          }
        }
      }
    }
  }
}
