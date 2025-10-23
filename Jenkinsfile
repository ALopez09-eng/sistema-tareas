pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Verificar Instalaciones') {
            steps {
                script {
                    sh '''
                        echo "=== Verificando herramientas ==="
                        codeql --version || echo "CodeQL no instalado"
                        docker --version || echo "Docker no disponible"
                        echo "=== Contenido del proyecto ==="
                        ls -la
                    '''
                }
            }
        }
        
        stage('Prueba Simple') {
            steps {
                script {
                    echo "✅ Pipeline funcionando correctamente"
                    sh 'echo "Build exitoso - $(date)" > build-success.txt'
                }
            }
        }
    }
    
    post {
        success {
            echo "🎉 ¡Jenkins reinstalado y funcionando!"
            archiveArtifacts artifacts: 'build-success.txt', fingerprint: true
        }
    }
}