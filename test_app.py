"""
Script para probar que la app se puede importar sin errores
"""
import sys

try:
    print("Importando app...")
    from app import app
    print("✓ App importada correctamente")
    
    print("\nVerificando routers...")
    print(f"✓ App configurada: {app.title}")
    
    print("\n✓ Todo está correcto. El servidor debería iniciar sin problemas.")
    
except Exception as e:
    print(f"✗ Error al importar app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

