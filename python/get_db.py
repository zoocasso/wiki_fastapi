import config

import pymysql
db_connection = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                             user=config.DATABASE_CONFIG['user'],
                             password=config.DATABASE_CONFIG['password'],
                             database=config.DATABASE_CONFIG['dbname'],
                             cursorclass=pymysql.cursors.DictCursor)
cursor = db_connection.cursor()

def get_seealso():
    cursor.execute("select * from seealso_tb")
    db_connection.commit()
    rows = cursor.fetchall()
    return rows

def get_section():
    cursor.execute("select * from section_tb")
    db_connection.commit()
    rows = cursor.fetchall()
    return rows

def get_xtools():
    cursor.execute("select * from xtools_tb")
    db_connection.commit()
    rows = cursor.fetchall()
    return rows