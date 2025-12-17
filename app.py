import os
from __init__ import create_app

app = create_app()

# Ruta de prueba simple
@app.route('/test')
def test():
    return "¡Funciona! 🎉"