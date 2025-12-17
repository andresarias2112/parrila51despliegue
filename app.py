import os
from __init__ import create_app

app = create_app()

# NO ejecutar app.run() en producción
# Gunicorn se encargará de esto