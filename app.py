from flask import Flask, render_template, request, redirect, url_for, jsonify
import pyodbc
import ConectionDB

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





# ---------- INICIO ----------
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
