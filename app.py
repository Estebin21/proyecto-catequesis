from flask import Flask, render_template, request, redirect, url_for, jsonify
import pyodbc
import ConectionDB
from collections import defaultdict

app = Flask(__name__)

# ----------LISTAR CATEQUIZANDOS----------
@app.route('/catequizandos/Listar')
def listar_catequizandos():
    conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
    try:
        SQL_QUERY = "{CALL Consultas.sp_ConsultarCatequizando}"
        cursor = conexion.cursor()
        cursor.execute(SQL_QUERY)
        contenido = cursor.fetchall()
        return render_template('catequizandos/Listar.html', catequizandos=contenido)
    except Exception as e:
        return f"Error al conectar a la base de datos: {e}", 500
    finally:
        if conexion:
            conexion.close()


# ---------- BUSCAR CATEQUIZANDO POR APELLIDO ----------
@app.route('/catequizandos/buscar', methods=['GET', 'POST'])
def buscar_catequizandos():
    catequizandos = []
    if request.method == 'POST':
        apellido = request.form["filtro_apellido"]
        if apellido:
            SQL_QUERY = "{CALL Consultas.sp_BuscarCatequizando (?)}"
            conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
            cursor = conexion.cursor()
            cursor.execute(SQL_QUERY, (apellido,))
            catequizandos = cursor.fetchall()
            conexion.close()
    return render_template('catequizandos/buscar.html', catequizandos=catequizandos)


# ---------- CREAR CATEQUIZANDO ----------
@app.route('/catequizandos/crear', methods=['GET', 'POST'])
def crear_catequizando():
    if request.method == 'POST':
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        cedula = request.form["cedula"]
        certificado = request.form["certificado"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        nivel_id = request.form["nivel_id"]
        persona_id = request.form["persona_id"]

        SQL_QUERY = "{CALL Consultas.sp_InsertarCatequizando (?, ?, ?, ?, ?, ?, ?)}"
        conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
        cursor = conexion.cursor()
        cursor.execute(SQL_QUERY, (nombre, apellido, cedula, certificado, fecha_nacimiento, nivel_id, persona_id))
        conexion.commit()
        conexion.close()
        return redirect(url_for('buscar_catequizandos'))

    return render_template('catequizandos/crear.html')

# ---------- EDITAR CATEQUIZANDO ----------
@app.route('/catequizandos/editar', methods=['GET', 'POST'])
def editar_catequizando():
    conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
    cursor = conexion.cursor()

    if request.method == 'POST':
        if "nombre" in request.form:  # actualiza
            id = int(request.form["id"])
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            SQL_QUERY = "{CALL Consultas.sp_ActualizarCatequizando (?, ?, ?)}"
            cursor.execute(SQL_QUERY, (id, nombre, apellido))
            conexion.commit()
            conexion.close()
            return redirect(url_for('buscar_catequizandos'))
        else:  # buscar por ID
            id = int(request.form["filtro_id"])
            SQL_QUERY = "SELECT Id_catequizando, Nombre, Apellido FROM Catequizando.Catequizando WHERE Id_catequizando = ?"
            cursor.execute(SQL_QUERY, (id,))
            catequizando = cursor.fetchone()
            conexion.close()
            return render_template('catequizandos/editar.html', catequizando=catequizando)

    return render_template('catequizandos/editar.html', catequizando=None)



# ---------- ELIMINAR CATEQUIZANDO ----------
@app.route('/catequizandos/eliminar', methods=['GET', 'POST'])
def eliminar_catequizando():
    conexion = pyodbc.connect(ConectionDB.ObtenerConexion())
    cursor = conexion.cursor()

    if request.method == 'POST':
        if "confirmar" in request.form:
            id = int(request.form["id"])
            SQL_QUERY = "{CALL Consultas.sp_EliminarCatequizando (?)}"
            cursor.execute(SQL_QUERY, (id,))
            conexion.commit()
            conexion.close()
            return redirect(url_for('buscar_catequizandos'))
        else:  # buscar por ID
            id = int(request.form["filtro_id"])
            SQL_QUERY = "SELECT * FROM Catequizando.Catequizando WHERE Id_catequizando = ?"
            cursor.execute(SQL_QUERY, (id,))
            catequizando = cursor.fetchone()
            conexion.close()
            return render_template('catequizandos/eliminar.html', catequizando=catequizando)

    return render_template('catequizandos/eliminar.html', catequizando=None)

# ---------- REPORTES REALIZADOS ----------
@app.route('/catequizandos/reporte', methods=['GET'])
def reporteCatequizando():
    colecciones = ConectionDB.setUpDBConnection()
    catequizandos = colecciones[0]
    catequistas = colecciones[1]
    certificados = colecciones[2]
    niveles = colecciones[3]
    parroquias = colecciones[4]
    db=colecciones[0].database
    niveles_dict = {n['_id']: n['nombre'] for n in niveles.find()}

    # Reporte 1: Catequizandos por parroquia
    parroquia_dict = {p['_id']: p['nombre'] for p in parroquias.find()}
    catequizandos_por_parroquia = []
    for doc in db.vista_catequizandos_por_parroquia.find():
        catequizandos_por_parroquia.append({
            "parroquia": parroquia_dict.get(doc["_id"], "Sin nombre"),
            "catequizandos": doc["catequizandos"]
        })

    # Reporte 2: Catequistas por parroquia
    catequistas_por_parroquia = []
    for doc in db.vista_catequistas_por_parroquia.find():
        catequistas_por_parroquia.append({
            "nombre": doc["nombre_completo"],
            "parroquia": parroquia_dict.get(doc.get("parroquia_id"), "No asignada")
        })

    # Reporte 3: Catequistas por nivel
    catequistas_por_nivel = []
    for doc in db.vista_catequistas_por_nivel.find():
        catequistas_por_nivel.append({
            "nivel": niveles_dict.get(doc["_id"], "Sin nombre"),
            "catequistas": doc["catequistas"]
        })

    # Reporte 4: Catequizandos por nivel
    catequizandos_por_nivel = []
    for doc in db.vista_catequizandos_por_nivel.find():
        catequizandos_por_nivel.append({
            "nivel": niveles_dict.get(doc["_id"], "Sin nombre"),
            "catequizandos": doc["catequizandos"]
        })

    return render_template(
        'catequizandos/reportes.html',
        catequizandos_por_parroquia=catequizandos_por_parroquia,
        catequistas_por_parroquia=catequistas_por_parroquia,
        catequistas_por_nivel=catequistas_por_nivel,
        catequizandos_por_nivel=catequizandos_por_nivel
    )


# ---------- INICIO ----------
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
