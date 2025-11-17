from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session, current_app
from app import bcrypt
import os
import sqlite3

tienda_bp = Blueprint("tienda_bp", __name__)

@tienda_bp.route("/tienda")
def tienda():
    conn = get_db_connection()
    libros = conn.execute("SELECT * FROM libro").fetchall()
    conn.close()
    return render_template('tienda.html', libros=libros)

@tienda_bp.route("/compra")
def compra():
    return render_template('compra.html')

@tienda_bp.route("/api/libros", methods=["GET"])
def get_libros():
    conn = get_db_connection()
    libros = conn.execute("SELECT * FROM libro").fetchall()
    conn.close()
    return jsonify([dict(lib) for lib in libros])

@tienda_bp.route("/api/libros/<int:id>", methods=["GET"])
def get_libro(id):
    conn = get_db_connection()
    lib = conn.execute("SELECT * FROM libro WHERE id = ?", (id)).fetchone()
    conn.close()
    if lib is None:
        return jsonify({"Error": "Libro no encontrado"}), 404
    return jsonify(dict(lib))

@tienda_bp.route("/api/libros/<int:id>", methods=["PUT"])
def update_libro(id):
    datos = request.get_json()
    conn = get_db_connection()
    conn.execute("UPDATE libro SET precio = ? WHERE id = ?", (datos.get("precio"), id))
    conn.commit()
    conn.close()
    return jsonify({"Mensaje": f"Libro con id {id} actualizado"})

@tienda_bp.route("/api/libros", methods=["POST"])
def add_libro():
    nuevo = request.get_json()
    conn = get_db_connection()
    conn.execute("INSERT INTO libro (nombre, autor, descripcion, precio) VALUES (?, ?, ?, ?)",
               (nuevo.get("nombre"), nuevo.get("autor"), nuevo.get("descripcion"), nuevo.get("precio")))
    
    conn.commit()
    conn.close()
    return jsonify({"Mensaje": "Libro agregado exitosamente"}), 201


def get_db_connection():
    conn = sqlite3.connect('libreria.db', timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout=5000')
    return conn

def close_db(exception=None):
    return None