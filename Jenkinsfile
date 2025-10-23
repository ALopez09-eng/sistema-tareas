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
        
        stage('Verificar y Configurar Permisos') {
            steps {
                script {
                    echo "🔧 Configurando permisos..."
                    
                    sh '''
                        # Verificar y configurar CodeQL
                        echo "=== Configurando CodeQL ==="
                        sudo chmod +x /usr/local/bin/codeql/codeql 2>/dev/null || true
                        sudo chmod -R 755 /usr/local/bin/codeql/ 2>/dev/null || true
                        
                        # Verificar CodeQL
                        /usr/local/bin/codeql/codeql --version || echo "⚠️ CodeQL no accesible"
                        
                        # Verificar Docker
                        echo "=== Configurando Docker ==="
                        docker --version || echo "⚠️ Docker no disponible"
                        
                        # Verificar grupo docker
                        groups | grep docker || echo "⚠️ Usuario no en grupo docker"
                    '''
                }
            }
        }
        
        stage('Análisis de Código - CodeQL') {
            steps {
                script {
                    echo "🔍 Iniciando análisis estático con CodeQL..."
                    
                    sh '''
                        # Usar ruta completa para CodeQL
                        /usr/local/bin/codeql/codeql database create codeql-db --language=python --source-root . || {
                            echo "⚠️ Falló creación de BD CodeQL, continuando..."
                        }
                        
                        /usr/local/bin/codeql/codeql database analyze codeql-db --format=sarif-latest --output=codeql-results.sarif || {
                            echo "⚠️ Falló análisis CodeQL, continuando..."
                        }
                        
                        echo "✅ Análisis CodeQL intentado"
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "🐳 Construyendo imagen Docker..."
                    
                    sh '''
                        # Construir imagen
                        docker build -t ${PROJECT_NAME}:latest . || {
                            echo "❌ Falló construcción Docker"
                            exit 1
                        }
                        echo "✅ Imagen Docker construida"
                    '''
                }
            }
        }
        
        stage('Despliegue Simple') {
            steps {
                script {
                    echo "🚀 Desplegando aplicación..."
                    
                    sh '''
                        # Detener contenedor anterior
                        docker stop ${PROJECT_NAME}-simple 2>/dev/null || true
                        docker rm ${PROJECT_NAME}-simple 2>/dev/null || true
                        
                        # Ejecutar nuevo contenedor
                        docker run -d --name ${PROJECT_NAME}-simple -p 5000:5000 ${PROJECT_NAME}:latest || {
                            echo "❌ No se pudo ejecutar contenedor"
                            exit 1
                        }
                        
                        echo "✅ Aplicación desplegada en: http://localhost:5000"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Limpiando recursos..."
            sh '''
                # Limpiar contenedores temporales
                docker stop ${PROJECT_NAME}-simple 2>/dev/null || true
                docker rm ${PROJECT_NAME}-simple 2>/dev/null || true
                
                echo "✅ Limpieza completada"
            '''
        }
        
        success {
            echo "🎉 Pipeline ejecutado exitosamente!"
        }
        
        failure {
            echo "💥 Pipeline falló - Revisar configuración de permisos"
        }
    }
}