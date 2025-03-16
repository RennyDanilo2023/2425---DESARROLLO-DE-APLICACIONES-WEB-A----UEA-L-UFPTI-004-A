import os
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_mysqldb import MySQL
from conexion.conexion import conectar

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'desarrollo_web'
app.config['SECRET_KEY'] = 'mi_clave_secreta'

# Inicializar la conexión con MySQL
mysql = MySQL(app)

# Definición del formulario con Flask-WTF
class MiFormulario(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=50)])
    mail = StringField('Correo', validators=[DataRequired(), Length(min=5, max=100)])
    edad = IntegerField('Edad', validators=[DataRequired(), NumberRange(min=1, max=120)])
    submit = SubmitField('Enviar')

# Ruta para comprobar la conexión
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

# Ruta para manejar el formulario y guardar datos en MySQL
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = MiFormulario()
    if form.validate_on_submit():
        nombre = form.nombre.data
        mail = form.mail.data
        edad = form.edad.data

        # Guardar en MySQL
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, mail, edad) VALUES (%s, %s, %s)", (nombre, mail, edad))
        conexion.commit()
        cursor.close()
        conexion.close()

        return render_template('resultado.html', nombre=nombre, mail=mail, edad=edad)
    return render_template('formulario.html', form=form)

# Ruta para mostrar los datos almacenados en MySQL
@app.route('/datos')
def ver_datos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios")
    datos_sql = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('datos.html', datos_sql=datos_sql)

# Ruta "Acerca de"
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

