import oracledb
import os
import uuid

oracledb.init_oracle_client(lib_dir=r"C:\oraclexe\app\oracle\instantclient-basic-windows.x64-11.2.0.4.0\instantclient_11_2")


#Insert row into table
def insert_row(row):

    conn = oracledb.connect(
    user="juan",
    password="3112",
    dsn="localhost:1521/XE"
    )
    print("connected")
    
    cursor = conn.cursor()

    id = uuid.uuid4().int
    id_actual = int(str(id)[:16])

    DML_INSERT = '''
    INSERT INTO SPEECH_TO_TEXT(ID,SENTENCE)
    VALUES(:id,:sentence)
    '''

    cursor.execute(DML_INSERT,id=id_actual, sentence=row) 
    print("Fila insertada correctamente")

    conn.commit()