import pyodbc
import json
from pymongo import MongoClient
import pyodbc

def ObtenerConexion():
    with open('config.json', 'r') as archivo_config:
        config = json.load(archivo_config)
    name_server = config['name_server']
    database = config['database']
    username = config['username']
    password = config['password']
    controlador_odbc = config['controlador_odbc']

    # 4. Crear Cadena de Conexión (con login SQL)
    connection_string = f'DRIVER={controlador_odbc};SERVER={name_server};DATABASE={database};UID={username};PWD={password}'
    return connection_string

def setUpDBConnection():

    uri = "mongodb+srv://sebasalmeida:udla@clusterudla01.hxj4agb.mongodb.net/?retryWrites=true&w=majority&appName=ClusterUDLA01"

    client = MongoClient(uri)

    db= client['Quito_Catequesis_DB_2025']
    coleccionCatequizandos = db['catequizandos']
    colleccionCatequistas = db['catequistas']
    colleccionCertificados = db['certificados']
    colleccionNiveles = db['niveles']
    colleccionParroquias = db['parroquias']
    
    return(coleccionCatequizandos, colleccionCatequistas, colleccionCertificados, colleccionNiveles, colleccionParroquias)