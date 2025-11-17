from flask import Blueprint, render_template, redirect, url_for, request

main = Blueprint("main", __name__)


@main.route('/')
def root():
    return redirect(url_for('main.inicio'))

@main.route('/inicio')
def inicio():
    return render_template('index.html', nombre="Librería Yenny")

@main.route('/about')
def about():
    return render_template('about.html', nosotros="Sobre nosotros")

@main.app_errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404

@main.route('/procesar', methods=['POST'])
def procesar():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    return render_template('resultado.html', nombre=nombre, apellido=apellido, correo=correo)


