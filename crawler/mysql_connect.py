import mysql.connector
import os

config = {
    'user': os.environ.get('DB_USER') or 'root',
    'password': os.environ.get('DB_PASSWORD') or 'root',
    'host': os.environ.get('MYSQL_HOST') or 'crawler-mysql5',
    'database': os.environ.get('DB_NAME') or 'test',
    'port': 3306
}

def createDatabase(name):
    connectConfig = config
    del connectConfig['database']
    try:
        mydb = mysql.connector.connect(**connectConfig)
        mycursor = mydb.cursor()
        mycursor.execute("DROP DATABASE IF EXISTS {}; CREATE DATABASE {};".format(name))
    except mysql.connector.Error as err:
        print("Error connecting Mysql: {}".format(err))

def getMysqlConnection():
    try:
        return mysql.connector.connect(**config)

    except mysql.connector.Error as err:
        print("Error connecting Mysql: {}".format(err))
