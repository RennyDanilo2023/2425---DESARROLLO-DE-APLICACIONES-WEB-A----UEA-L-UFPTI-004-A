import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from conexion.conexion import conectar

# Configuración de la aplicación Flask
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'desarrollo_web'
app.config['SECRET_KEY'] = 'clave_secreta'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Modelo de Usuario para Flask-Login
class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password_hash):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario, nombre, email, password_hash FROM usuarios WHERE id_usuario = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conexion.close()

    if user:
        return Usuario(*user)
    return None

# Formularios de Registro e Inicio de Sesión
class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Correo', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

# Ruta de prueba de conexión
@app.route('/test_db')
def test_db():
    conexion = conectar()
    if conexion:
        conexion.close()
        return "✅ Conexión exitosa a la base de datos MySQL."
    else:
        return "❌ Error al conectar a la base de datos."

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registrar usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        email = form.email.data
        password = form.password.data
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, email, password_hash) VALUES (%s, %s, %s)",
                       (nombre, email, password_hash))
        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Usuario registrado correctamente. ¡Inicia sesión!', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html', form=form)

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_usuario, nombre, email, password_hash FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conexion.close()

        # Depuración: Imprimir usuario obtenido de la base de datos
        print("Usuario encontrado en la base de datos:", user)

        if user:
            stored_hash = user[3]  # Obtener hash almacenado
            if stored_hash and bcrypt.check_password_hash(stored_hash, password):
                usuario = Usuario(*user)
                login_user(usuario)
                return redirect(url_for('dashboard'))
            else:
                flash('Contraseña incorrecta', 'danger')
        else:
            flash('Usuario no encontrado', 'danger')

    return render_template('login.html', form=form)

# Ruta protegida (requiere login)
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Bienvenido, {current_user.nombre} <br><a href='/logout'>Cerrar sesión</a>"

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Ruta "Acerca de"
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)


