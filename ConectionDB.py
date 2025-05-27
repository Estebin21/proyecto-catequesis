import pyodbc
import json
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