pipeline {
    agent any

    environment {
        REPORT_DIR = "reports/windows/build_${BUILD_NUMBER}"
        PYTHON = "C:\\Users\\ontar\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10')) // Keep only last 10 builds
        timestamps() // Add timestamps in console logs
    }

    stages {

        stage('Checkout') {
            steps {
                git url: 'https://github.com/luckyjoy/hyperscale_ssd.git', branch: 'main'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat "${PYTHON} -m pip install --upgrade pip"
                bat "${PYTHON} -m pip install -r requirements.txt"
            }
        }

        stage('Prepare Report Directory') {
            steps {
                bat "mkdir \"${REPORT_DIR}\""
            }
        }

        stage('Run Behave Tests') {
            steps {
                script {
                    // Prepare Behave command
                    def behaveCommand = "${PYTHON} -m behave --tags=@all --exclude \"features/manual_tests/.*\" -f html-pretty -o \"${REPORT_DIR}/validation_report.html\""

                    // Run Behave and capture exit code (do not fail pipeline immediately)
                    def exitCode = bat(script: behaveCommand, returnStatus: true)

                    // Edit HTML report if it exists
                    def reportFile = "${REPORT_DIR}/validation_report.html"
                    if (fileExists(reportFile)) {
                        def content = readFile(reportFile)

                        // Update HTML title with build number
                        content = content.replace(
                            "<title>Behave Report</title>",
                            "<title>Behave Test Report - Build ${BUILD_NUMBER}</title>"
                        )

                        // Inject CSS for pass/fail color coding & dark mode
                        def cssInjection = """
                        <style>
                            .passed { color: green; font-weight: bold; }
                            .failed { color: red; font-weight: bold; }
                            .skipped { color: orange; font-weight: bold; }
                            .undefined { color: gray; font-weight: bold; }
                            body { background-color: #1e1e1e; color: #ffffff; }
                        </style>
                        """.stripIndent()

                        content = content.replace("</head>", "${cssInjection}</head>")
                        writeFile file: reportFile, text: content
                    }

                    // Mark build UNSTABLE if tests failed
                    if (exitCode != 0) {
                        unstable("⚠️ Behave tests failed with exit code ${exitCode}")
                    } else {
                        echo "✅ All Behave tests passed!"
                    }
                }
            }
        }

        stage('Publish HTML Report') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: "${REPORT_DIR}",
                    reportFiles: 'validation_report.html',
                    reportName: "Behave Test Report - Build ${BUILD_NUMBER}",
                    reportTitles: "SSD Hyperscale Validation - Build ${BUILD_NUMBER}"
                ])
            }
        }

        stage('Archive Report Artifacts') {
            steps {
                archiveArtifacts artifacts: "${REPORT_DIR}/**/*", fingerprint: true
            }
        }
    }

    post {
        always {
            echo "📄 HTML report is available in Jenkins."
        }
        success {
            echo "🎉 Pipeline completed successfully!"
        }
        unstable {
            echo "⚠️ Pipeline is UNSTABLE due to test failures. Check the report!"
        }
        failure {
            echo "❌ Pipeline failed due to unexpected errors."
        }
    }
}
