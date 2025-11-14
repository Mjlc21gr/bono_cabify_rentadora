#!/usr/bin/env python3
"""
Script de pruebas para la API Cabify
Ejecuta pruebas contra la API local o desplegada
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuración
LOCAL_URL = "http://localhost:8080"
DEPLOYED_URL = "https://cabify-api-XXXXXXX.run.app"  # Cambiar por tu URL real


def test_endpoint(base_url: str, endpoint: str, method: str = "GET", data: Dict[Any, Any] = None) -> bool:
    """Prueba un endpoint específico"""
    url = f"{base_url}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)

        print(f"🧪 {method} {endpoint}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Success")
                if isinstance(result, dict) and 'data' in result:
                    print(f"   📄 Data: {result.get('message', 'No message')}")
                return True
            except json.JSONDecodeError:
                print(f"   ✅ Success (non-JSON response)")
                return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False

    except requests.RequestException as e:
        print(f"   ❌ Connection error: {str(e)}")
        return False

    print()


def run_tests(base_url: str):
    """Ejecuta todas las pruebas"""
    print(f"🚀 Ejecutando pruebas contra: {base_url}")
    print("=" * 50)

    tests_passed = 0
    total_tests = 0

    # Test 1: Root endpoint
    total_tests += 1
    if test_endpoint(base_url, "/"):
        tests_passed += 1

    # Test 2: Health check
    total_tests += 1
    if test_endpoint(base_url, "/health"):
        tests_passed += 1

    # Test 3: Validar cobertura
    total_tests += 1
    cobertura_data = {
        "placa": "RPW203",
        "correo": "luis.gomez@segurosbolivar.com",
        "perdio_movilidad": "No",
        "gestor": "luis.gomez@segurosbolivar.com"
    }
    if test_endpoint(base_url, "/validar-cobertura", "POST", cobertura_data):
        tests_passed += 1

    # Test 4: Generar bono
    total_tests += 1
    bono_data = {
        "id": "42",
        "numero_siniestro": "15100032",
        "correo": "luis.gomez@segurosbolivar.com"
    }
    if test_endpoint(base_url, "/generar-bono", "POST", bono_data):
        tests_passed += 1

    # Test 5: Programar taller
    total_tests += 1
    taller_data = {
        "id": "42",
        "numero_siniestro": "15100032",
        "correo": "luis.gomez@segurosbolivar.com",
        "fecha_programado": "2025-02-28"
    }
    if test_endpoint(base_url, "/programar-taller", "POST", taller_data):
        tests_passed += 1

    # Test 6: Generar bono programado
    total_tests += 1
    bono_programado_data = {
        "id": "42",
        "numero_siniestro": "15100032",
        "placa": "RPW203",
        "gestor": "luis.gomez@segurosbolivar.com"
    }
    if test_endpoint(base_url, "/generar-bono-programado", "POST", bono_programado_data):
        tests_passed += 1

    # Resultados
    print("=" * 50)
    print(f"📊 Resultados: {tests_passed}/{total_tests} pruebas exitosas")

    if tests_passed == total_tests:
        print("🎉 ¡Todas las pruebas pasaron!")
        return True
    else:
        print("⚠️  Algunas pruebas fallaron")
        return False


def main():
    """Función principal"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "local":
            success = run_tests(LOCAL_URL)
        elif sys.argv[1] == "deployed":
            success = run_tests(DEPLOYED_URL)
        else:
            print("Uso: python test_api.py [local|deployed]")
            sys.exit(1)
    else:
        print("🔍 Probando ambos endpoints...")
        print("\n1. API Local:")
        local_success = run_tests(LOCAL_URL)

        print("\n2. API Desplegada:")
        deployed_success = run_tests(DEPLOYED_URL)

        success = local_success or deployed_success

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()