from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from __init__ import mysql, mail, serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
import uuid

# -------------------- BLUEPRINT --------------------
auth_bp = Blueprint('auth', __name__)

# -------------------- PÁGINA PRINCIPAL (HOME) --------------------
@auth_bp.route('/')
def home():
    """Página principal con información del restaurante"""
    return render_template("index.html")


# -------------------- LOGIN --------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ✅ Usar .get() para evitar KeyError
        correo = request.form.get('txtCorreo', '').strip()
        password = request.form.get('txtPassword', '').strip()
        
        # Validar que no estén vacíos
        if not correo or not password:
            flash("❌ Por favor completa todos los campos", "danger")
            return render_template("login.html")

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
            user = cur.fetchone()
            cur.close()

            if user and check_password_hash(user['contraseña'], password):
                if user['estado'].lower() != 'activo':
                    flash("⚠️ Cuenta inactiva. Revisa tu correo para activarla", "warning")
                    return redirect(url_for('auth.login'))

                session['logueado'] = True
                session['id_usuario'] = user['id_usuario']
                session['nombre'] = user['nombre']
                session['apellido'] = user['apellido']
                session['rol'] = user['rol']

                flash(f"✅ Bienvenido {user['nombre']} {user['apellido']}", "success")

                if session['rol'] == 'administrador':
                    return redirect(url_for('admin.admin_dashboard'))
                elif session['rol'] == 'empleado':
                    return redirect(url_for('empleado.empleado_dashboard'))
                elif session['rol'] == 'cliente':
                    return redirect(url_for('dashboard.cliente_dashboard'))
            else:
                flash("❌ Correo o contraseña incorrectos", "danger")
        except Exception as e:
            flash(f"❌ Error en el sistema: {str(e)}", "danger")
            print(f"Error en login: {e}")

    return render_template("login.html")


# -------------------- REGISTRO --------------------
@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # ✅ Usar .get() para evitar KeyError
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validar campos obligatorios
        if not all([nombre, apellido, correo, password]):
            flash("❌ Por favor completa todos los campos obligatorios", "danger")
            return render_template('registro.html')
        
        try:
            # Verificar si el correo ya existe
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
            existe = cur.fetchone()
            
            if existe:
                flash("⚠️ Este correo ya está registrado", "warning")
                cur.close()
                return redirect(url_for('auth.registro'))
            
            # Hash de la contraseña
            password_hash = generate_password_hash(password)
            
            # IMPORTANTE: Siempre asignar rol 'cliente' por defecto
            rol = 'cliente'
            
            token = str(uuid.uuid4())

            cur.execute("""
                INSERT INTO usuarios (nombre, apellido, telefono, direccion, correo, contraseña, rol, estado, token_activacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'inactivo', %s)
            """, (nombre, apellido, telefono, direccion, correo, password_hash, rol, token))
            mysql.connection.commit()
            cur.close()

            try:
                enlace = url_for('auth.activar_cuenta', token=token, _external=True)
                msg = Message('📧 Activa tu cuenta - Parrilla 51',
                              sender='enviodecorreosparrilla51@gmail.com',
                              recipients=[correo])
                msg.body = f"""
Hola {nombre},

Gracias por registrarte en Parrilla 51 🍖

Haz clic en el siguiente enlace para activar tu cuenta:
{enlace}

Si no solicitaste este registro, ignora este correo.
"""
                mail.send(msg)
                flash("✅ Registro exitoso. Revisa tu correo para activar tu cuenta", "success")
            except Exception as e:
                print(f"Error enviando correo: {e}")
                flash("⚠️ Usuario creado pero no se pudo enviar el correo de activación", "warning")

            return redirect(url_for('auth.login'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f"❌ Error al registrar: {str(e)}", "danger")
            print(f"Error en registro: {e}")

    return render_template('registro.html')


# -------------------- ACTIVAR CUENTA --------------------
@auth_bp.route('/activar/<token>')
def activar_cuenta(token):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE token_activacion = %s", (token,))
        user = cur.fetchone()

        if user:
            cur.execute("""
                UPDATE usuarios SET estado = 'activo', token_activacion = NULL
                WHERE id_usuario = %s
            """, (user['id_usuario'],))
            mysql.connection.commit()
            flash("✅ Cuenta activada exitosamente. Ya puedes iniciar sesión", "success")
        else:
            flash("❌ El enlace de activación es inválido o ya fue usado", "danger")
        
        cur.close()
    except Exception as e:
        flash(f"❌ Error al activar cuenta: {str(e)}", "danger")
        print(f"Error en activación: {e}")
    
    return redirect(url_for('auth.login'))


# -------------------- OLVIDÉ CONTRASEÑA --------------------
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # ✅ Usar .get() para evitar KeyError
        correo = request.form.get('email', '').strip()
        
        if not correo:
            flash("❌ Por favor ingresa tu correo electrónico", "danger")
            return render_template("forgot_password.html")

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
            user = cur.fetchone()

            if user:
                try:
                    token = serializer.dumps(correo, salt='password-reset-salt')
                    enlace = url_for('auth.reset_password', token=token, _external=True)

                    msg = Message('🔑 Restablecer contraseña - Parrilla 51',
                                  sender='enviodecorreosparrilla51@gmail.com',
                                  recipients=[correo])
                    msg.body = f"""Hola,

Para restablecer tu contraseña, haz clic en el siguiente enlace:
{enlace}

Si no solicitaste este cambio, ignora este mensaje."""
                    mail.send(msg)

                    flash("✅ Correo de recuperación enviado exitosamente", "success")
                except Exception as e:
                    flash("❌ Error al enviar el correo. Intenta nuevamente", "danger")
                    print(f"Error: {e}")
            else:
                flash("⚠️ El correo no está registrado", "warning")
            
            cur.close()
        except Exception as e:
            flash(f"❌ Error en el sistema: {str(e)}", "danger")
            print(f"Error en forgot_password: {e}")
        
        return redirect(url_for('auth.login'))

    return render_template("forgot_password.html")


# -------------------- RESTABLECER CONTRASEÑA --------------------
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        correo = serializer.loads(token, salt='password-reset-salt', max_age=900)
    except Exception:
        flash("❌ El enlace es inválido o ha expirado", "danger")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        # ✅ Usar .get() para evitar KeyError
        password1 = request.form.get('password1', '').strip()
        password2 = request.form.get('password2', '').strip()
        
        if not password1 or not password2:
            flash("❌ Por favor completa todos los campos", "danger")
            return redirect(request.url)

        if password1 != password2:
            flash("⚠️ Las contraseñas no coinciden", "warning")
            return redirect(request.url)

        try:
            hashed = generate_password_hash(password1)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE usuarios SET contraseña = %s WHERE correo = %s", (hashed, correo))
            mysql.connection.commit()
            cur.close()

            flash("✅ Contraseña restablecida exitosamente", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"❌ Error al cambiar contraseña: {str(e)}", "danger")
            print(f"Error en reset_password: {e}")

    return render_template("reset_password.html")


# -------------------- CERRAR SESIÓN --------------------
@auth_bp.route('/logout')
def logout():
    nombre = session.get('nombre', 'Usuario')
    session.clear()
    flash(f"👋 Hasta pronto {nombre}. Sesión cerrada correctamente", "info")
    return redirect(url_for('auth.login'))


# -------------------- REGISTRAR BLUEPRINT --------------------
def init_app(app):
    app.register_blueprint(auth_bp)