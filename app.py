from flask import Flask, render_template, request, redirect, url_for, jsonify
import pyodbc
import ConectionDB

app = Flask(__name__)

# ---------- API JSON: LISTAR CATEQUISTAS POR APELLIDO ----------
@app.route('/api/catequistas')
def listar_catequistas_json():
    SQL_QUERY = "{CALL Consultas.sp_BuscarCatequista (?)}"
    apellido = request.args.get("apellido", "")
    conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
    cursor = conexion.cursor()
    cursor.execute(SQL_QUERY, (apellido,))
    columnas = [column[0] for column in cursor.description]
    resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    conexion.close()
    return jsonify(resultados)

# ---------- API JSON: BUSCAR CATEQUISTA POR APELLIDO ----------
@app.route('/api/catequistas/buscar', methods=['GET'])
def buscar_catequista_json():
    apellido = request.args.get("apellido")
    if not apellido:
        return jsonify({"error": "Apellido no proporcionado"}), 400

    SQL_QUERY = "{CALL Consultas.sp_BuscarCatequista (?)}"
    conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
    cursor = conexion.cursor()
    cursor.execute(SQL_QUERY, (apellido,))
    filas = cursor.fetchall()
    columnas = [column[0] for column in cursor.description] if filas else []
    conexion.close()

    if filas:
        resultados = [dict(zip(columnas, fila)) for fila in filas]
        return jsonify(resultados)
    else:
        return jsonify({"message": "No se encontraron catequistas con ese apellido"}), 404

# ---------- HTML: BUSCAR CATEQUISTA POR APELLIDO ----------
@app.route('/catequistas', methods=['GET', 'POST'])
def buscar_catequistas():
    catequistas = []
    if request.method == 'POST':
        apellido = request.form["filtro_apellido"]
        if apellido:
            SQL_QUERY = "{CALL Consultas.sp_BuscarCatequista (?)}"
            conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
            cursor = conexion.cursor()
            cursor.execute(SQL_QUERY, (apellido,))
            catequistas = cursor.fetchall()
            conexion.close()
    return render_template('catequistas/buscar.html', catequistas=catequistas)

# ---------- CREAR CATEQUISTA ----------
@app.route('/catequistas/crear', methods=['GET', 'POST'])
def crear_catequista():
    if request.method == 'POST':
        cedula = request.form["cedula"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        tipo = request.form["tipo"]
        correo = request.form["correo"]
        parroquia_id = request.form["parroquia_id"]

        conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Catequista.Catequista 
            (Nombre, Apellido, Cedula, Fecha_nacimiento, Tipo, Correo, Parroquia_Id_parroquia)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (nombre, apellido, cedula, fecha_nacimiento, tipo, correo, parroquia_id))
        conexion.commit()
        conexion.close()
        return redirect(url_for('buscar_catequistas'))

    return render_template('catequistas/crear.html')

# ---------- EDITAR CATEQUISTA ----------
@app.route('/catequistas/editar/<int:id>', methods=['GET', 'POST'])
def editar_catequista(id):
    conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
    cursor = conexion.cursor()

    if request.method == 'POST':
        cedula = request.form["cedula"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        tipo = request.form["tipo"]
        correo = request.form["correo"]
        parroquia_id = request.form["parroquia_id"]

        cursor.execute("""
            UPDATE Catequista.Catequista SET 
            Nombre = ?, Apellido = ?, Cedula = ?, Fecha_nacimiento = ?, Tipo = ?, 
            Correo = ?, Parroquia_Id_parroquia = ?
            WHERE Id_catequesis = ?""",
            (nombre, apellido, cedula, fecha_nacimiento, tipo, correo, parroquia_id, id))
        conexion.commit()
        conexion.close()
        return redirect(url_for('buscar_catequistas'))

    cursor.execute("SELECT * FROM Catequista.Catequista WHERE Id_catequesis = ?", (id,))
    catequista = cursor.fetchone()
    conexion.close()
    return render_template('catequistas/editar.html', catequista=catequista)

# ---------- ELIMINAR CATEQUISTA ----------
@app.route('/catequistas/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_catequista(id):
    conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
    cursor = conexion.cursor()

    if request.method == 'POST':
        cursor.execute("DELETE FROM Catequista.Catequista WHERE Id_catequesis = ?", (id,))
        conexion.commit()
        conexion.close()
        return redirect(url_for('buscar_catequistas'))

    cursor.execute("SELECT * FROM Catequista.Catequista WHERE Id_catequesis = ?", (id,))
    catequista = cursor.fetchone()
    conexion.close()
    return render_template('catequistas/eliminar.html', catequista=catequista)

# ---------- CONSULTAR CATEQUIZANDOS (usa SP) ----------
@app.route('/catequizandos')
def BuscarCatequizando():
    conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
    try:
        SQL_QUERY = "{CALL Consultas.sp_ConsultarCatequizando}"
        cursor = conexion.cursor()
        cursor.execute(SQL_QUERY)
        contenido = cursor.fetchall()
        return render_template('catequizando.html', catequizandos=contenido)
    except Exception as e:
        return f"Error al conectar a la base de datos: {e}", 500
    finally:
        if conexion:
            conexion.close()

# ---------- INICIO ----------
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
