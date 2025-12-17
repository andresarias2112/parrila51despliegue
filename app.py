import os
from __init__ import create_app

app = create_app()

if __name__ == "__main__":
    # Solo para desarrollo local, Railway usará Gunicorn
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)