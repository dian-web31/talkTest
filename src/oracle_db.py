import oracledb
import os

oracledb.init_oracle_client(lib_dir=r"C:\oraclexe\app\oracle\instantclient-basic-windows.x64-11.2.0.4.0\instantclient_11_2")

def insert_row(license_plates, type_vehicle):
    try:
        conn = oracledb.connect(
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            dsn=os.getenv('DATABASE_DSN')
        )
        print("Conectado a la base de datos")
        
        cursor = conn.cursor()

        DML_INSERT = '''
        INSERT INTO PARKING_LOT(LICENSE_PLATES, TYPE_VEHICLE)
        VALUES(:license_plates, :type_vehicle)
        '''

        cursor.execute(DML_INSERT, license_plates=license_plates, type_vehicle=type_vehicle) 
        print("Fila insertada correctamente")

        conn.commit()
        return True

    except oracledb.Error as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False

    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

    finally:
        # Asegurarse de cerrar la conexión
        if 'conn' in locals():
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada")