pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'localhost:5000'
        PROJECT_NAME = 'sistema-tareas'
        GITHUB_CREDENTIALS = credentials('github-token')
        SMTP_CREDENTIALS = credentials('smtp-credentials')
        DEPENDENCY_TRACK_API_KEY = credentials('dependency-track-api-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git config user.email "jenkins@example.com"'
                sh 'git config user.name "Jenkins"'
            }
        }
        
        stage('Análisis de Código - CodeQL') {
            steps {
                script {
                    echo "Iniciando análisis estático con CodeQL..."
                    
                    // Configurar CodeQL
                    sh '''
                        codeql database create codeql-db --language=python --source-root .
                    '''
                    
                    // Ejecutar análisis
                    sh '''
                        codeql database analyze codeql-db --format=sarif-latest --output=codeql-results.sarif
                    '''
                    
                    // Verificar resultados
                    def hasErrors = false
                    if (fileExists('codeql-results.sarif')) {
                        def results = readFile file: 'codeql-results.sarif'
                        if (results.contains('"level": "error"')) {
                            hasErrors = true
                            error "❌ CodeQL encontró vulnerabilidades críticas. Pipeline detenido."
                        }
                    }
                    
                    if (!hasErrors) {
                        echo "✅ Análisis CodeQL completado sin errores críticos"
                    }
                }
            }
        }
        
        stage('Análisis de Seguridad - Bandit') {
            steps {
                script {
                    echo "Ejecutando análisis de seguridad con Bandit..."
                    sh '''
                        pip install bandit
                        bandit -r . -f html -o bandit-report.html || true
                    '''
                }
            }
        }
        
        stage('Análisis de Dependencias - Safety') {
            steps {
                script {
                    echo "Analizando dependencias con Safety..."
                    sh '''
                        pip install safety
                        safety check --json > safety-report.json || true
                    '''
                }
            }
        }
        
        stage('Análisis con Dependency-Track') {
            steps {
                script {
                    echo "Generando Bill of Materials..."
                    sh '''
                        # Generar BOM con CycloneDX
                        pip install cyclonedx-bom
                        cyclonedx-py -r -i requirements.txt -o bom.xml
                        
                        # Subir BOM a Dependency-Track
                        curl -X "POST" "http://dependency-track:8080/api/v1/bom" \\
                            -H "Content-Type: application/json" \\
                            -H "X-API-Key: ${DEPENDENCY_TRACK_API_KEY}" \\
                            -d "{
                                \\"project\\": \\"${PROJECT_NAME}-${BUILD_NUMBER}\",
                                \\"bom\\": \\"$(cat bom.xml | base64 | tr -d '\\n')\\"
                            }"
                    '''
                    
                    // Esperar análisis
                    sleep time: 120, unit: 'SECONDS'
                    
                    // Obtener reporte
                    sh '''
                        curl -X "GET" "http://dependency-track:8080/api/v1/finding/project/latest" \\
                            -H "X-API-Key: ${DEPENDENCY_TRACK_API_KEY}" \\
                            -o dependency-findings.json
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Construyendo imagen Docker..."
                    sh """
                        docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}:${BUILD_NUMBER} .
                        docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest .
                    """
                }
            }
        }
        
        stage('Test de Imagen Docker') {
            steps {
                script {
                    echo "Ejecutando tests en contenedor..."
                    sh """
                        docker run -d --name test-container -p 5001:5000 ${DOCKER_REGISTRY}/${PROJECT_NAME}:${BUILD_NUMBER}
                        sleep 10
                        
                        # Test de salud
                        curl -f http://localhost:5001/ || {
                            docker logs test-container
                            docker stop test-container
                            docker rm test-container
                            error "❌ La aplicación no responde correctamente"
                        }
                        
                        docker stop test-container
                        docker rm test-container
                    """
                }
            }
        }
        
        stage('Despliegue en Desarrollo') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    echo "Desplegando en entorno de desarrollo..."
                    sh """
                        docker stop ${PROJECT_NAME}-dev || true
                        docker rm ${PROJECT_NAME}-dev || true
                        docker run -d --name ${PROJECT_NAME}-dev -p 5000:5000 ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest
                    """
                }
            }
        }
        
        stage('Despliegue en Producción') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "Desplegando en producción..."
                    sh """
                        docker stop ${PROJECT_NAME}-prod || true
                        docker rm ${PROJECT_NAME}-prod || true
                        docker run -d --name ${PROJECT_NAME}-prod -p 80:5000 ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest
                    """
                }
            }
        }
        
        stage('Generar Reportes') {
            steps {
                script {
                    echo "Generando reportes consolidados..."
                    
                    // Generar reporte HTML combinado
                    sh '''
                        echo "<html><body><h1>Reporte de Seguridad - Build ${BUILD_NUMBER}</h1>" > security-report.html
                        echo "<h2>CodeQL</h2><pre>" >> security-report.html
                        if [ -f codeql-results.sarif ]; then
                            cat codeql-results.sarif | head -50 >> security-report.html
                        else
                            echo "No se encontraron resultados de CodeQL" >> security-report.html
                        fi
                        echo "</pre><h2>Bandit</h2>" >> security-report.html
                        if [ -f bandit-report.html ]; then
                            cat bandit-report.html >> security-report.html
                        else
                            echo "<p>No se encontró reporte de Bandit</p>" >> security-report.html
                        fi
                        echo "</body></html>" >> security-report.html
                    '''
                    
                    // Convertir a PDF con Pandoc
                    sh '''
                        pandoc security-report.html -o security-report.pdf
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo "Limpiando recursos temporales..."
            sh '''
                docker system prune -f || true
                rm -f codeql-db || true
            '''
            
            // Archivar reportes
            archiveArtifacts artifacts: '*.html,*.pdf,*.json,*.sarif', fingerprint: true
        }
        
        success {
            echo "✅ Pipeline ejecutado exitosamente"
            
            // Enviar email de éxito
            emailext (
                to: 'proyectoricardo21@gmail.com',
                subject: "✅ Pipeline Exitoso - ${PROJECT_NAME} - Build ${BUILD_NUMBER}",
                body: """
                El pipeline CI/CD se ha ejecutado correctamente.
                
                Proyecto: ${PROJECT_NAME}
                Build: ${BUILD_NUMBER}
                Estado: EXITOSO
                Branch: ${env.BRANCH_NAME}
                Commit: ${env.GIT_COMMIT}
                
                Se adjuntan los reportes de seguridad generados.
                """,
                attachmentsPattern: 'security-report.pdf, bandit-report.html, safety-report.json'
            )
        }
        
        failure {
            echo "❌ Pipeline falló"
            
            // Enviar email de error
            emailext (
                to: 'proyectoricardo21@gmail.com',
                subject: "❌ Pipeline Fallido - ${PROJECT_NAME} - Build ${BUILD_NUMBER}",
                body: """
                El pipeline CI/CD ha fallado.
                
                Proyecto: ${PROJECT_NAME}
                Build: ${BUILD_NUMBER}
                Estado: FALLIDO
                Branch: ${env.BRANCH_NAME}
                Commit: ${env.GIT_COMMIT}
                
                Revisa los logs en Jenkins para más detalles.
                """,
                attachLog: true
            )
        }
        
        unstable {
            echo "⚠️ Pipeline inestable"
        }
    }
}