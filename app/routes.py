from flask import Blueprint, render_template, redirect, url_for, request, jsonify, g, flash, session
from . import bcrypt
import sqlite3

main = Blueprint("main", __name__)
tienda_bp = Blueprint("tienda_bp", __name__)
cuenta = Blueprint("cuenta", __name__)

DATABASE = "libreria.db"



def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, timeout=10, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA busy_timeout = 5000")
    return g.db

def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()



@main.route('/')
def root():
    return redirect(url_for('main.inicio'))

@main.route('/inicio')
def inicio():
    return render_template('index.html', nombre="Librería Yenny")

@main.route('/about')
def about():
    return render_template('about.html', nosotros="Sobre nosotros")

@tienda_bp.route("/tienda")
def tienda():
    db = get_db()
    libros = db.execute("SELECT * FROM libro").fetchall()
    return render_template('tienda.html', libros=libros)

@main.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404

@main.route('/procesar', methods=['POST'])
def procesar():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    return render_template('resultado.html', nombre=nombre, apellido=apellido, correo=correo)

@tienda_bp.route("/compra")
def compra():
    return render_template('compra.html')

@tienda_bp.route("/api/libros", methods=["GET"])
def get_libros():
    db = get_db()
    libros = db.execute("SELECT * FROM libro").fetchall()
    return jsonify([dict(lib) for lib in libros])

@tienda_bp.route("/api/libros/<int:id>", methods=["GET"])
def get_libro(id):
    db = get_db()
    lib = db.execute("SELECT * FROM libro WHERE id = ?", (id,)).fetchone()
    if lib is None:
        return jsonify({"Error": "Libro no encontrado"}), 404
    return jsonify(dict(lib))

@tienda_bp.route("/api/libros/<int:id>", methods=["PUT"])
def update_libro(id):
    datos = request.get_json()
    db = get_db()
    db.execute("UPDATE libro SET precio = ? WHERE id = ?", (datos.get("precio"), id))
    db.commit()
    return jsonify({"Mensaje": f"Libro con id {id} actualizado"})

@tienda_bp.route("/api/libros", methods=["POST"])
def add_libro():
    nuevo = request.get_json()
    db = get_db()
    db.execute("INSERT INTO libro (nombre, autor, descripcion, precio) VALUES (?, ?, ?, ?)",
               (nuevo.get("nombre"), nuevo.get("autor"), nuevo.get("descripcion"), nuevo.get("precio")))
    
    db.commit()
    return jsonify({"Mensaje": "Libro agregado exitosamente"}), 201

@cuenta.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        mail = request.form.get("mail")
        contraseña = request.form.get("contraseña")
        contraseña_hash = bcrypt.generate_password_hash(contraseña).decode("utf-8")

        db = get_db()
        db.execute(
            "INSERT INTO cliente (nombre, apellido, mail, contraseña) VALUES (?, ?, ?, ?)",
            (nombre, apellido, mail, contraseña_hash),
        )
        db.commit()

        session["cliente_id"] = db.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]

        session["cliente_nombre"] = nombre
        return redirect(url_for("cuenta.registro_exitoso"))
    return render_template("registro.html")

@cuenta.route("/registro_exitoso")
def registro_exitoso():
    return render_template("registro_exitoso.html")


@cuenta.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mail = request.form.get('mail')
        contraseña = request.form.get('contraseña')

        db = get_db()
        cliente = db.execute(
            "SELECT * FROM cliente WHERE mail = ?",
            (mail,)
        ).fetchone()

        if cliente and bcrypt.check_password_hash(cliente["contraseña"], contraseña):
            session["cliente_id"] = cliente["id"]
            session["cliente_nombre"] = cliente["nombre"]
            return redirect(url_for("cuenta.logueo_exitoso"))
        else:
            flash("Email o contraseña incorrectos")
            return render_template("login.html")

    return render_template("login.html")

@cuenta.route("/logueo_exitoso")
def logueo_exitoso():
    if "cliente_id" not in session:     
        return redirect(url_for("cuenta.login"))

    nombre = session.get("cliente_nombre") 
    return render_template("logueo_exitoso.html", nombre=nombre)

@cuenta.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for("cuenta.login"))



