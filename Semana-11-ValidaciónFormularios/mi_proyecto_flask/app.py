from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'

# Definición del formulario con Flask-WTF
class MiFormulario(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=50)])
    edad = IntegerField('Edad', validators=[DataRequired(), NumberRange(min=1, max=120)])
    submit = SubmitField('Enviar')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = MiFormulario()
    if form.validate_on_submit():
        nombre = form.nombre.data
        edad = form.edad.data
        return render_template('resultado.html', nombre=nombre, edad=edad)
    return render_template('formulario.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
