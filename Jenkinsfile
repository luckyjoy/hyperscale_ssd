pipeline {
    agent any

    environment {
        PYTHON = "C:\\Users\\ontar\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
        REPORT_BASE = "reports\\windows"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/luckyjoy/hyperscale_ssd.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat "${env.PYTHON} -m pip install --upgrade pip"
                bat "${env.PYTHON} -m pip install -r requirements.txt"
            }
        }

        stage('Prepare Report Directories') {
            steps {
                script {
                    // Create a unique report folder for each build
                    env.REPORT_DIR = "${env.REPORT_BASE}\\build_${BUILD_NUMBER}"
                    bat "mkdir ${env.REPORT_DIR}"
                }
            }
        }

        stage('Run Behave Tests') {
            steps {
                script {
                    def behaveReport = "${env.REPORT_DIR}\\validation_report.html"
                    try {
                        bat "${env.PYTHON} -m behave --tags=@adv --exclude \"features/manual_tests/.*\" -f html-pretty -o ${behaveReport}"
                        env.BEHAVE_STATUS = "PASS"
                    } catch (err) {
                        env.BEHAVE_STATUS = "FAILED"
                    }
                }
            }
        }

        stage('Publish HTML Report') {
            steps {
                script {
                    // Publish HTML report
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: env.REPORT_DIR,
                        reportFiles: 'validation_report.html',
                        reportName: "Behave Test Report - Build ${BUILD_NUMBER}"
                    ])

                    // Colorize status for console output
                    def color = env.BEHAVE_STATUS == "PASS" ? "green" : "red"
                    echo "\u001B[38;5;10m✅ \u001B[0mBehave Test Report URL: https://localhost:8443/job/SSD_Hyperscale/${BUILD_NUMBER}/htmlreports/${BUILD_NUMBER}/validation_report.html"
                    echo "Status: \u001B[38;5;${color}m${env.BEHAVE_STATUS}\u001B[0m"
                }
            }
        }

        stage('Archive Screenshots') {
            steps {
                archiveArtifacts artifacts: 'screenshots/**/*.*', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            echo "Pipeline finished. Build Status: ${currentBuild.currentResult}"
        }
    }
}
