from flask import Flask, render_template, request, redirect, url_for, flash

from db import get_connection

import psycopg2.extras


app = Flask(__name__)

app.secret_key = "clave-secreta"


# Página de inicio
@app.route("/")
def inicio():
    return render_template("inicio.html")


# Listar productos
@app.route("/productos")
def productos():

    conexion = get_connection()

    cursor = conexion.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cursor.execute("""
        SELECT id, codigo, nombre, categoria,
               precio, existencia, activo
        FROM producto
        ORDER BY id DESC
    """)

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "productos.html",
        productos=productos
    )


# Crear producto
@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():

    if request.method == "POST":

        codigo = request.form["codigo"]
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        precio = request.form["precio"]
        existencia = request.form["existencia"]

        activo = request.form.get("activo") == "on"

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO producto
            (codigo, nombre, categoria, precio, existencia, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            codigo,
            nombre,
            categoria,
            precio,
            existencia,
            activo
        ))

        conexion.commit()

        cursor.close()
        conexion.close()

        flash("Producto creado correctamente.", "success")

        return redirect(url_for("productos"))

    return render_template("form.html")


# Editar producto
@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):

    conexion = get_connection()

    cursor = conexion.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    if request.method == "POST":

        codigo = request.form["codigo"]
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        precio = request.form["precio"]
        existencia = request.form["existencia"]

        activo = request.form.get("activo") == "on"

        cursor.execute("""
            UPDATE producto
            SET codigo = %s,
                nombre = %s,
                categoria = %s,
                precio = %s,
                existencia = %s,
                activo = %s
            WHERE id = %s
        """, (
            codigo,
            nombre,
            categoria,
            precio,
            existencia,
            activo,
            id
        ))

        conexion.commit()

        cursor.close()
        conexion.close()

        flash("Producto actualizado correctamente.", "success")

        return redirect(url_for("productos"))

    cursor.execute("""
        SELECT id, codigo, nombre, categoria,
               precio, existencia, activo
        FROM producto
        WHERE id = %s
    """, (id,))

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if producto is None:

        flash("Producto no encontrado.", "danger")

        return redirect(url_for("productos"))

    return render_template(
        "form.html",
        producto=producto
    )


# Eliminar producto
@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):

    conexion = get_connection()

    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM producto
        WHERE id = %s
    """, (id,))

    conexion.commit()

    cursor.close()
    conexion.close()

    flash("Producto eliminado correctamente.", "success")

    return redirect(url_for("productos"))


# Buscar productos
@app.route("/productos/buscar")
def buscar_productos():

    texto = request.args.get("q", "")

    conexion = get_connection()

    cursor = conexion.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cursor.execute("""
        SELECT id, codigo, nombre, categoria,
               precio, existencia, activo
        FROM producto
        WHERE codigo ILIKE %s
           OR nombre ILIKE %s
           OR categoria ILIKE %s
        ORDER BY id DESC
    """, (
        f"%{texto}%",
        f"%{texto}%",
        f"%{texto}%"
    ))

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "buscar.html",
        productos=productos,
        texto=texto
    )


if __name__ == "__main__":
    app.run(debug=True)