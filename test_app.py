from __init__ import create_app

print("PROBANDO LA APP")

try:
    app = create_app()
    print("APP FUNCIONA")
except Exception as e:
    print("ERROR:", e)