pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_NAME = 'sistema-tareas'
        DOCKER_TAG = 'latest'
    }
    
    stages {
        stage('Declarative: Checkout SCM') {
            steps {
                checkout scm
            }
        }
        
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: 'https://github.com/ALopez09-eng/sistema-tareas.git']]
                ])
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
        
        stage('Security Scan') {
            steps {
                script {
                    sh '''
                        echo "🔍 Ejecutando análisis de seguridad..."
                        codeql --version || echo "CodeQL no disponible"
                        # Aquí puedes agregar comandos CodeQL específicos cuando esté instalado
                        # codeql database create codeql-db --language=python
                        # codeql database analyze codeql-db --format=sarif-latest --output=codeql-results.sarif
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                        echo "🐳 Construyendo imagen Docker..."
                        docker build -t $DOCKER_IMAGE_NAME:$DOCKER_TAG .
                        echo "✅ Imagen Docker construida: $DOCKER_IMAGE_NAME:$DOCKER_TAG"
                    '''
                }
            }
        }
        
        stage('Prueba Simple') {
            steps {
                script {
                    echo "✅ Pipeline funcionando correctamente"
                    sh '''
                        date
                        echo "Build exitoso - $(date)"
                    '''
                }
            }
        }
        
        stage('Listar Imágenes Docker') {
            steps {
                script {
                    sh '''
                        echo "📦 Imágenes Docker disponibles:"
                        docker images | grep $DOCKER_IMAGE_NAME || echo "No se encontró la imagen $DOCKER_IMAGE_NAME"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo "🎉 ¡Jenkins reinstalado y funcionando!"
            archiveArtifacts artifacts: '**/*.py, **/requirements.txt, **/Dockerfile', fingerprint: true
        }
        success {
            sh '''
                echo "✅ BUILD EXITOSO - $(date)"
                docker images | head -10
            '''
        }
        failure {
            echo "❌ BUILD FALLIDO - Revisar logs"
        }
    }
}