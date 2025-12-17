import os
from __init__ import create_app

try:
    app = create_app()
    print("✅ App creada exitosamente")
except Exception as e:
    print(f"❌ Error al crear app: {e}")
    import traceback
    traceback.print_exc()
    raise