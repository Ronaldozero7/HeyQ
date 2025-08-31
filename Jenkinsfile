pipeline {
  agent any
  options { timestamps() }
  stages {
  stage('Setup') {
      steps {
        sh 'python3 -m venv .venv'
        sh '. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt'
        sh '. .venv/bin/activate && python -m spacy download en_core_web_sm'
        sh '. .venv/bin/activate && python -m playwright install --with-deps'
      }
    }
    stage('Test') {
      steps {
        sh '. .venv/bin/activate && pytest -n auto --html=heyq/reports/report.html --self-contained-html'
      }
      post {
        always {
          archiveArtifacts artifacts: 'heyq/reports/**', fingerprint: true
          junit '**/junit*.xml'
        }
      }
    }
  }
}
