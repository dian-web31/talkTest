import oracledb
import os

oracledb.init_oracle_client(lib_dir=r"C:\oraclexe\app\oracle\instantclient-basic-windows.x64-11.2.0.4.0\instantclient_11_2")
#Funcion para insertar una fila en la base de datos que es numero de matricula y typo de vehiculo
def insert_row(license_plates, type_vehicle):
    try:
        #Maneja la conexion con la base de datos 
        conn = oracledb.connect(
            user=os.getenv('DATABASE_USER'), # Usuario de la base de datos.
            password=os.getenv('DATABASE_PASSWORD'), # Contraseña del usuario.
            dsn=os.getenv('DATABASE_DSN') #Nombre de red (DSN) para conectarse a la base de datos (puede incluir host, puerto y servicio).
        )
        print("Conectado a la base de datos") #Mensaje de conexion a la base de datos
        
        cursor = conn.cursor() #Objeto para ejecutar sentencias SQL.

        #Se inicializa la sentencia SQL de insert para ingresar los datos en la base de datos
        DML_INSERT = '''
        INSERT INTO PARKING_LOT(LICENSE_PLATES, TYPE_VEHICLE)
        VALUES(:license_plates, :type_vehicle)
        '''
        #Se ejecuta la sentencia SQL de insert y se agrega la placa y el tipo de vehiculo
        cursor.execute(DML_INSERT, license_plates=license_plates, type_vehicle=type_vehicle) 
        print("Fila insertada correctamente")

        conn.commit()
        return True #Retorna verdadero si se inserta correctamente

    #Manejo de errores en la base de Datos
    except oracledb.Error as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False

    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

    finally:
        # Asegurarse de cerrar la conexión satisfactoriamente
        if 'conn' in locals():
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada")