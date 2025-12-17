#!/usr/bin/env python3
"""
Script para arreglar el campo contraseña en Railway
Ejecuta: python fix_database.py
"""

from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# Configuración de Railway (usa las variables de entorno)
app.config['MYSQL_HOST'] = os.getenv('MYSQLHOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQLUSER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQLPASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQLDATABASE', 'railway')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQLPORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        print("=" * 60)
        print("🔧 ARREGLANDO BASE DE DATOS")
        print("=" * 60)
        
        # 1. Ver tamaño actual
        print("\n1️⃣ Verificando tamaño actual del campo contraseña...")
        cur.execute("""
            SELECT CHARACTER_MAXIMUM_LENGTH 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'railway'
            AND TABLE_NAME = 'usuarios' 
            AND COLUMN_NAME = 'contraseña'
        """)
        result = cur.fetchone()
        if result:
            tamaño_actual = result['CHARACTER_MAXIMUM_LENGTH']
            print(f"   📏 Tamaño actual: {tamaño_actual} caracteres")
        
        # 2. Cambiar a VARCHAR(255)
        print("\n2️⃣ Cambiando a VARCHAR(255)...")
        cur.execute("ALTER TABLE usuarios MODIFY COLUMN contraseña VARCHAR(255)")
        mysql.connection.commit()
        print("   ✅ Campo actualizado correctamente")
        
        # 3. Verificar el cambio
        print("\n3️⃣ Verificando cambio...")
        cur.execute("""
            SELECT CHARACTER_MAXIMUM_LENGTH 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'railway'
            AND TABLE_NAME = 'usuarios' 
            AND COLUMN_NAME = 'contraseña'
        """)
        result = cur.fetchone()
        if result:
            tamaño_nuevo = result['CHARACTER_MAXIMUM_LENGTH']
            print(f"   📏 Nuevo tamaño: {tamaño_nuevo} caracteres")
            
            if tamaño_nuevo == 255:
                print("\n   ✅ ¡ÉXITO! El campo ahora puede almacenar hashes completos")
            else:
                print(f"\n   ⚠️ El tamaño es {tamaño_nuevo}, debería ser 255")
        
        # 4. Mostrar estado de usuarios
        print("\n4️⃣ Estado de contraseñas de usuarios:")
        cur.execute("""
            SELECT 
                id_usuario,
                nombre,
                correo,
                LENGTH(contraseña) as longitud,
                LEFT(contraseña, 20) as inicio_hash
            FROM usuarios
            LIMIT 5
        """)
        usuarios = cur.fetchall()
        
        if usuarios:
            for user in usuarios:
                print(f"   - {user['correo']}: {user['longitud']} chars - {user['inicio_hash']}...")
        else:
            print("   ⚠️ No hay usuarios en la base de datos")
        
        print("\n" + "=" * 60)
        print("🎉 PROCESO COMPLETADO")
        print("=" * 60)
        print("\n💡 Ahora puedes:")
        print("   1. Registrar un nuevo usuario")
        print("   2. Intentar hacer login")
        print("   3. Si sigue fallando, ejecuta test_hash.py para diagnóstico\n")
        
        cur.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()