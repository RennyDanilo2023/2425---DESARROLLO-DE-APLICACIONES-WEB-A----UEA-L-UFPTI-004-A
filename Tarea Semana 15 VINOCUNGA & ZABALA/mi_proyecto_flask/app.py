import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from conexion.conexion import conectar

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'desarrollo_web'
app.config['SECRET_KEY'] = 'clave_secreta'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ✅ Permitir usar current_user en HTML
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Modelo de usuario
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

# Formularios
class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Correo', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

# Rutas
@app.route('/test_db')
def test_db():
    conexion = conectar()
    if conexion:
        conexion.close()
        return "✅ Conexión exitosa a la base de datos MySQL."
    else:
        return "❌ Error al conectar a la base de datos."

@app.route('/')
def index():
    return render_template('index.html')

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

        if user:
            stored_hash = user[3]
            if stored_hash and bcrypt.check_password_hash(stored_hash, password):
                usuario = Usuario(*user)
                login_user(usuario)
                return redirect(url_for('dashboard'))
            else:
                flash('Contraseña incorrecta', 'danger')
        else:
            flash('Usuario no encontrado', 'danger')

    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

# CRUD de productos
@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']

        if not nombre or not precio or not stock:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('crear_producto'))

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)",
                           (nombre, precio, stock))
            conexion.commit()
            cursor.close()
            conexion.close()
            flash('Producto registrado exitosamente.', 'success')
            return redirect(url_for('listar_productos'))
        except Exception as e:
            flash(f'Error al registrar producto: {e}', 'danger')
            return redirect(url_for('crear_producto'))

    return render_template('formulario_producto.html')

@app.route('/productos')
@login_required
def listar_productos():
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template('lista_productos.html', productos=productos)
    except Exception as e:
        flash(f'Error al obtener productos: {e}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']

        cursor.execute("UPDATE productos SET nombre=%s, precio=%s, stock=%s WHERE id_producto=%s",
                       (nombre, precio, stock, id))
        conexion.commit()
        cursor.close()
        conexion.close()
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('listar_productos'))

    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()

    if producto:
        return render_template('formulario_producto.html', producto=producto)
    else:
        flash('Producto no encontrado.', 'warning')
        return redirect(url_for('listar_productos'))

@app.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    flash('Producto eliminado correctamente.', 'success')
    return redirect(url_for('listar_productos'))

if __name__ == '__main__':
    app.run(debug=True)
