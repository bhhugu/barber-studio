from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "barberia_secret"

DATABASE = "barberia.db"

def conectar():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        telefono TEXT,
        fecha TEXT,
        hora TEXT,
        descripcion TEXT,
        estado TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS galeria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        url TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS precios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        servicio TEXT,
        precio TEXT
    )
    """)

    conn.commit()
    conn.close()

crear_tablas()

USUARIO_ADMIN = "admin"
PASSWORD_ADMIN = "1234"

# HOME
@app.route("/")
def inicio():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM galeria")
    galeria = cursor.fetchall()
    cursor.execute("SELECT * FROM precios")
    precios = cursor.fetchall()
    conn.close()
    return render_template("index.html", galeria=galeria, precios=precios)

# CITAS
@app.route("/citas")
def citas():
    return render_template("citas.html")

# GUARDAR CITA
@app.route("/guardar_cita", methods=["POST"])
def guardar_cita():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO citas (nombre, telefono, fecha, hora, descripcion, estado)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form["nombre"],
        request.form["telefono"],
        request.form["fecha"],
        request.form["hora"],
        request.form["descripcion"],
        "Pendiente"
    ))
    conn.commit()
    conn.close()
    return redirect("/")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        if (
            request.form["usuario"] == USUARIO_ADMIN and
            request.form["password"] == PASSWORD_ADMIN
        ):
            session["admin"] = True
            return redirect("/admin")
        else:
            error = "Datos incorrectos"
    return render_template("login.html", error=error)

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# PANEL ADMIN
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citas")
    citas = cursor.fetchall()
    cursor.execute("SELECT * FROM galeria")
    galeria = cursor.fetchall()
    cursor.execute("SELECT * FROM precios")
    precios = cursor.fetchall()
    conn.close()

    total = len(citas)
    aceptadas = len([c for c in citas if c["estado"] == "Aceptada"])
    canceladas = len([c for c in citas if c["estado"] == "Cancelada"])
    pendientes = len([c for c in citas if c["estado"] == "Pendiente"])

    return render_template(
        "admin.html",
        citas=citas,
        galeria=galeria,
        precios=precios,
        total=total,
        aceptadas=aceptadas,
        canceladas=canceladas,
        pendientes=pendientes
    )

# AGENDA PÚBLICA
@app.route("/mis_citas")
def mis_citas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citas")
    citas = cursor.fetchall()
    conn.close()

    dias = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    meses = {
        "January": "Enero", "February": "Febrero", "March": "Marzo",
        "April": "Abril", "May": "Mayo", "June": "Junio",
        "July": "Julio", "August": "Agosto", "September": "Septiembre",
        "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
    }

    citas_bonitas = []
    for cita in citas:
        cita = dict(cita)
        fecha_obj = datetime.strptime(cita["fecha"], "%Y-%m-%d")
        dia = dias[fecha_obj.strftime("%A")]
        numero = fecha_obj.day
        mes = meses[fecha_obj.strftime("%B")]
        cita["fecha_bonita"] = f"{dia} {numero} de {mes}"
        hora_obj = datetime.strptime(cita["hora"], "%H:%M")
        cita["hora_bonita"] = hora_obj.strftime("%I:%M %p")
        citas_bonitas.append(cita)

    return render_template("mis_citas.html", citas=citas_bonitas)

# ESTADOS
@app.route("/aceptar/<int:i>")
def aceptar(i):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE citas SET estado = ? WHERE id = ?", ("Aceptada", i))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/cancelar/<int:i>")
def cancelar(i):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE citas SET estado = ? WHERE id = ?", ("Cancelada", i))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/eliminar/<int:i>")
def eliminar(i):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM citas WHERE id = ?", (i,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# SUBIR FOTO
@app.route("/subir_foto", methods=["POST"])
def subir_foto():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO galeria (titulo, url) VALUES (?, ?)", (
        request.form["titulo"],
        request.form["url"]
    ))
    conn.commit()
    conn.close()
    return redirect("/admin")

# AGREGAR PRECIO
@app.route("/agregar_precio", methods=["POST"])
def agregar_precio():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO precios (servicio, precio) VALUES (?, ?)", (
        request.form["servicio"],
        request.form["precio"]
    ))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ELIMINAR PRECIO
@app.route("/eliminar_precio/<int:i>")
def eliminar_precio(i):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM precios WHERE id = ?", (i,))
    conn.commit()
    conn.close()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)