pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'sistema-tareas'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Verificar Instalaciones') {
            steps {
                script {
                    echo "🔍 Verificando herramientas instaladas..."
                    sh '''
                        echo "=== CodeQL ==="
                        codeql --version || echo "❌ CodeQL no disponible"
                        echo "=== Docker ==="
                        docker --version || echo "❌ Docker no disponible"
                        echo "=== Python ==="
                        python3 --version || echo "❌ Python3 no disponible"
                    '''
                }
            }
        }
        
        stage('Análisis de Código - CodeQL') {
            steps {
                script {
                    echo "🔍 Iniciando análisis estático con CodeQL..."
                    
                    sh '''
                        # Crear base de datos CodeQL
                        codeql database create codeql-db --language=python --source-root .
                        
                        # Analizar código
                        codeql database analyze codeql-db --format=sarif-latest --output=codeql-results.sarif
                        
                        echo "✅ Análisis CodeQL completado"
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "🐳 Construyendo imagen Docker..."
                    sh """
                        docker build -t ${PROJECT_NAME}:latest .
                    """
                }
            }
        }
        
        stage('Test de Imagen Docker') {
            steps {
                script {
                    echo "🧪 Probando imagen Docker..."
                    sh """
                        # Ejecutar contenedor de prueba
                        docker run -d --name test-container -p 5001:5000 ${PROJECT_NAME}:latest
                        sleep 10
                        
                        # Verificar que la aplicación responde
                        curl -f http://localhost:5001/ || {
                            echo "❌ La aplicación no responde correctamente"
                            docker logs test-container
                            exit 1
                        }
                        
                        echo "✅ Aplicación responde correctamente"
                        
                        # Limpiar contenedor de prueba
                        docker stop test-container
                        docker rm test-container
                    """
                }
            }
        }
        
        stage('Despliegue en Producción') {
            steps {
                script {
                    echo "🚀 Desplegando aplicación en producción..."
                    sh """
                        # Detener contenedor anterior si existe
                        docker stop ${PROJECT_NAME}-prod || true
                        docker rm ${PROJECT_NAME}-prod || true
                        
                        # Ejecutar nuevo contenedor
                        docker run -d --name ${PROJECT_NAME}-prod -p 5000:5000 ${PROJECT_NAME}:latest
                        
                        echo "✅ Aplicación desplegada en: http://localhost:5000"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Limpiando recursos temporales..."
            sh '''
                # Limpiar contenedores temporales
                docker stop test-container || true
                docker rm test-container || true
                
                # Limpiar imágenes temporales
                docker system prune -f || true
                
                # Limpiar base de datos CodeQL
                rm -rf codeql-db || true
            '''
        }
        
        success {
            echo "🎉 Pipeline ejecutado exitosamente!"
            
            // Enviar email de éxito (configura SMTP después)
            emailext (
                to: 'proyectoricardo21@gmail.com',
                subject: "✅ Pipeline Exitoso - ${PROJECT_NAME}",
                body: """
                El pipeline CI/CD se ha ejecutado correctamente.
                
                Proyecto: ${PROJECT_NAME}
                Estado: EXITOSO
                
                La aplicación está desplegada en: http://localhost:5000
                """
            )
        }
        
        failure {
            echo "💥 Pipeline falló - Revisar logs para detalles"
        }
    }
}