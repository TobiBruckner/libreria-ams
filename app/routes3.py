from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session, current_app
from app import bcrypt
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import sqlite3

cuenta = Blueprint("cuenta", __name__)

@cuenta.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        apellido = (request.form.get("apellido") or "").strip()
        mail = (request.form.get("mail") or request.form.get("correo") or "").strip()
        contraseña = (request.form.get("contraseña") or "").strip()

        if not (nombre and apellido and mail and contraseña):
            return render_template("registro.html", error="Completa todos los campos"), 400

        conn = get_db_connection()
        hashed = bcrypt.generate_password_hash(contraseña).decode('utf-8')
        conn.execute(
            "INSERT INTO cliente (nombre, apellido, mail, contraseña) VALUES (?, ?, ?, ?)",
            (nombre, apellido, mail, hashed),
        )
        conn.commit()
        conn.close()
        session["registro_info"] = {"nombre": nombre, "apellido": apellido, "email": mail}
        return redirect(url_for("cuenta.registro_exitoso"))
    return render_template("registro.html")

def _build_google_flow():
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = url_for('cuenta.auth_callback', _external=True)
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        redirect_uri=redirect_uri,
    )

@cuenta.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mail = (request.form.get("mail") or "").strip()
        contraseña = (request.form.get("contraseña") or "").strip()
        if not (mail and contraseña):
            return render_template("login.html", error="Completa todos los campos"), 400
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM cliente WHERE mail = ?",
            (mail,),
        ).fetchone()
        conn.close()
        if not user:
            return render_template("login.html", error="Credenciales inválidas"), 401
        stored = user["contraseña"]
        valid = False
        try:
            valid = bcrypt.check_password_hash(stored, contraseña)
        except Exception:
            valid = False
        if not valid and stored == contraseña:
            valid = True
        if not valid:
            return render_template("login.html", error="Credenciales inválidas"), 401
        session["user_info"] = {"name": user["nombre"], "email": user["mail"]}
        return redirect(url_for("cuenta.logueo_exitoso"))
    return render_template("login.html")

@cuenta.route("/login_google")
def login_google():
    flow = _build_google_flow()
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    session["code_verifier"] = flow.code_verifier
    print(f"OAuth redirect_uri: {flow.redirect_uri}")
    return redirect(authorization_url)

@cuenta.route("/auth/callback")
def auth_callback():
    if request.args.get("state") != session.get("state"):
        return "Error: State mismatch", 400
    flow = _build_google_flow()
    cv = session.get("code_verifier")
    if cv:
        flow.code_verifier = cv
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    try:
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, google_requests.Request(), current_app.config.get('GOOGLE_CLIENT_ID')
        )
    except ValueError:
        return "Error: Invalid token", 400
    session["user_info"] = {
        "name": id_info.get("name"),
        "email": id_info.get("email"),
        "picture": id_info.get("picture"),
    }
    return redirect(url_for("cuenta.logueo_exitoso"))

@cuenta.route("/logueo_exitoso")
def logueo_exitoso():
    return render_template("logueo_exitoso.html", user=session.get("user_info"))

@cuenta.route("/logout")
def logout():
    session.pop("user_info", None)
    return redirect(url_for("main.inicio"))

@cuenta.route("/registro_exitoso")
def registro_exitoso():
    return render_template("registro_exitoso.html", registro=session.get("registro_info"))


def get_db_connection():
    conn = sqlite3.connect('libreria.db', timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout=5000')
    return conn

def close_db(exception=None):
    return None