import os
import json
import csv
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_sqlalchemy import SQLAlchemy

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Ruta absoluta del proyecto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'usuarios.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mi_clave_secreta'

# Inicializar la base de datos (Asegurar que solo haya una instancia)
db = SQLAlchemy(app)

# Definir el modelo de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# Definición del formulario con Flask-WTF
class MiFormulario(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=50)])
    edad = IntegerField('Edad', validators=[DataRequired(), NumberRange(min=1, max=120)])
    submit = SubmitField('Enviar')

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar el formulario y guardar datos
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = MiFormulario()
    if form.validate_on_submit():
        nombre = form.nombre.data
        edad = form.edad.data

        # Guardar en TXT
        with open('datos/datos.txt', 'a') as f:
            f.write(f"{nombre}, {edad}\n")

        # Guardar en JSON
        datos_json = {'nombre': nombre, 'edad': edad}
        if os.path.exists('datos/datos.json'):
            with open('datos/datos.json', 'r') as f:
                data = json.load(f)
        else:
            data = []
        data.append(datos_json)
        with open('datos/datos.json', 'w') as f:
            json.dump(data, f, indent=4)

        # Guardar en CSV
        with open('datos/datos.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([nombre, edad])

        # Guardar en SQLite
        nuevo_usuario = Usuario(nombre=nombre, edad=edad)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return render_template('resultado.html', nombre=nombre, edad=edad)
    return render_template('formulario.html', form=form)

# Ruta para mostrar los datos almacenados
@app.route('/datos')
def ver_datos():
    # Leer datos desde archivos y la base de datos
    datos_txt, datos_json, datos_csv, datos_sqlite = [], [], [], []

    # Leer TXT
    if os.path.exists('datos/datos.txt'):
        with open('datos/datos.txt', 'r') as f:
            datos_txt = f.readlines()

    # Leer JSON
    if os.path.exists('datos/datos.json'):
        with open('datos/datos.json', 'r') as f:
            datos_json = json.load(f)

    # Leer CSV
    if os.path.exists('datos/datos.csv'):
        with open('datos/datos.csv', 'r') as f:
            reader = csv.reader(f)
            datos_csv = list(reader)

    # Leer SQLite
    datos_sqlite = Usuario.query.all()

    return render_template('datos.html', datos_txt=datos_txt, datos_json=datos_json, datos_csv=datos_csv, datos_sqlite=datos_sqlite)

# Ruta "Acerca de"
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
