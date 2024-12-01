import oracledb
import os
import uuid

oracledb.init_oracle_client(lib_dir=r"C:\instantclient_11_2")

def insert_row(row):
    try:
        conn = oracledb.connect(
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            dsn=os.getenv('DATABASE_DSN')
        )
        print("Conectado a la base de datos")
        
        cursor = conn.cursor()

        id = uuid.uuid4().int
        id_actual = int(str(id)[:16])

        DML_INSERT = '''
        INSERT INTO SPEECH_TO_TEXT(ID, SENTENCE)
        VALUES(:id, :sentence)
        '''

        cursor.execute(DML_INSERT, id=id_actual, sentence=row) 
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