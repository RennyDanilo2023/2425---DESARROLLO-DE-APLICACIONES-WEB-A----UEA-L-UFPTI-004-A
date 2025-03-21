import mysql.connector

def conectar():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='desarrollo_web'
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None
