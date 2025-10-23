#!/bin/bash

echo "🔍 Ejecutando escaneos de seguridad..."

# Bandit - Análisis estático de seguridad Python
echo "📊 Ejecutando Bandit..."
bandit -r . -f json -o bandit-report.json

# Safety - Verificación de vulnerabilidades en dependencias
echo "📦 Ejecutando Safety..."
safety check --json > safety-report.json

# Verificación de dependencias obsoletas
echo "🔄 Verificando dependencias obsoletas..."
pip list --outdated --format=json > outdated-dependencies.json

# Análisis de secrets en el código
echo "🔐 Buscando secrets en el código..."
git secrets --scan

echo "✅ Escaneos de seguridad completados"