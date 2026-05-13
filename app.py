from flask import Flask, render_template, request, redirect, session
import json
import os
import webbrowser
import threading
from datetime import datetime

app = Flask(__name__)
app.secret_key = "barberia_secret"

ARCHIVO_CITAS = "citas.json"
ARCHIVO_GALERIA = "galeria.json"
ARCHIVO_PRECIOS = "precios.json"

# CREAR ARCHIVOS
for archivo in [ARCHIVO_CITAS, ARCHIVO_GALERIA, ARCHIVO_PRECIOS]:
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            json.dump([], f)

USUARIO_ADMIN = "admin"
PASSWORD_ADMIN = "1234"

# HOME
@app.route("/")
def inicio():

    with open(ARCHIVO_GALERIA, "r") as f:
        galeria = json.load(f)

    with open(ARCHIVO_PRECIOS, "r") as f:
        precios = json.load(f)

    return render_template(
        "index.html",
        galeria=galeria,
        precios=precios
    )

# CITAS
@app.route("/citas")
def citas():
    return render_template("citas.html")

# GUARDAR CITA
@app.route("/guardar_cita", methods=["POST"])
def guardar_cita():

    nueva = {
        "nombre": request.form["nombre"],
        "telefono": request.form["telefono"],
        "fecha": request.form["fecha"],
        "hora": request.form["hora"],
        "descripcion": request.form["descripcion"],
        "estado": "Pendiente"
    }

    with open(ARCHIVO_CITAS, "r") as f:
        citas = json.load(f)

    citas.append(nueva)

    with open(ARCHIVO_CITAS, "w") as f:
        json.dump(citas, f, indent=4)

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

    with open(ARCHIVO_CITAS, "r") as f:
        citas = json.load(f)

    with open(ARCHIVO_GALERIA, "r") as f:
        galeria = json.load(f)

    with open(ARCHIVO_PRECIOS, "r") as f:
        precios = json.load(f)

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

    with open(ARCHIVO_CITAS, "r") as f:
        citas = json.load(f)

    dias = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    meses = {
        "January": "Enero",
        "February": "Febrero",
        "March": "Marzo",
        "April": "Abril",
        "May": "Mayo",
        "June": "Junio",
        "July": "Julio",
        "August": "Agosto",
        "September": "Septiembre",
        "October": "Octubre",
        "November": "Noviembre",
        "December": "Diciembre"
    }

    for cita in citas:

        # FORMATEAR FECHA
        fecha_obj = datetime.strptime(cita["fecha"], "%Y-%m-%d")

        dia = dias[fecha_obj.strftime("%A")]
        numero = fecha_obj.day
        mes = meses[fecha_obj.strftime("%B")]

        cita["fecha_bonita"] = f"{dia} {numero} de {mes}"

        # FORMATEAR HORA
        hora_obj = datetime.strptime(cita["hora"], "%H:%M")

        cita["hora_bonita"] = hora_obj.strftime("%I:%M %p")

    return render_template(
        "mis_citas.html",
        citas=citas
    )
# ESTADOS
@app.route("/aceptar/<int:i>")
def aceptar(i):

    with open(ARCHIVO_CITAS, "r") as f:
        citas = json.load(f)

    citas[i]["estado"] = "Aceptada"

    with open(ARCHIVO_CITAS, "w") as f:
        json.dump(citas, f, indent=4)

    return redirect("/admin")

@app.route("/cancelar/<int:i>")
def cancelar(i):

    with open(ARCHIVO_CITAS, "r") as f:
        citas = json.load(f)

    citas[i]["estado"] = "Cancelada"

    with open(ARCHIVO_CITAS, "w") as f:
        json.dump(citas, f, indent=4)

    return redirect("/admin")

@app.route("/eliminar/<int:i>")
def eliminar(i):

    with open(ARCHIVO_CITAS, "r") as f:
        citas = json.load(f)

    citas.pop(i)

    with open(ARCHIVO_CITAS, "w") as f:
        json.dump(citas, f, indent=4)

    return redirect("/admin")

# SUBIR FOTO
@app.route("/subir_foto", methods=["POST"])
def subir_foto():

    data = {
        "titulo": request.form["titulo"],
        "url": request.form["url"]
    }

    with open(ARCHIVO_GALERIA, "r") as f:
        galeria = json.load(f)

    galeria.append(data)

    with open(ARCHIVO_GALERIA, "w") as f:
        json.dump(galeria, f, indent=4)

    return redirect("/admin")

# AGREGAR PRECIO
@app.route("/agregar_precio", methods=["POST"])
def agregar_precio():

    servicio = request.form["servicio"]
    precio = request.form["precio"]

    with open(ARCHIVO_PRECIOS, "r") as f:
        precios = json.load(f)

    precios.append({
        "servicio": servicio,
        "precio": precio
    })

    with open(ARCHIVO_PRECIOS, "w") as f:
        json.dump(precios, f, indent=4)

    return redirect("/admin")

# ELIMINAR PRECIO
@app.route("/eliminar_precio/<int:i>")
def eliminar_precio(i):

    with open(ARCHIVO_PRECIOS, "r") as f:
        precios = json.load(f)

    precios.pop(i)

    with open(ARCHIVO_PRECIOS, "w") as f:
        json.dump(precios, f, indent=4)

    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)