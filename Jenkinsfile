pipeline {
  agent none
  stages {
    stage('SSD Hyperscale Tests') {
      matrix {
        axes { axis { name 'OS'; values 'linux', 'windows' } }
        agent { label "${OS}-agent" }
        stages {
          stage('Launch VM and Run Behave') {
            steps {
              script {
                if ("${OS}" == "windows") {
                  bat 'python qemu-faults\\qemu_launch_vm.py'
                  bat 'behave --tags=@windows features/ssd_fault_injection.feature'
                } else {
                  sh 'python3 qemu-faults/qemu_launch_vm.py'
                  sh 'behave --tags=@linux features/ssd_fault_injection.feature'
                }
              }
            }
          }
        }
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'reports/*.json', allowEmptyArchive: true
    }
  }
}