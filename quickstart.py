# import the required libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
from bs4 import BeautifulSoup
import mysql.connector

# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():

    ####################################
    ########## AUTH GMAIL API ##########
    ####################################

    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None

    # The file token.pickle contains the user access token.
    # Check if it exists
    if os.path.exists('token.pickle'):
        # Read the token from the file and store it in the variable creds
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the access token in token.pickle file for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Nos conectamos a la API de GMAIL
    service = build('gmail', 'v1', credentials=creds)

    ############################################
    ########## OBTENEMOS LOS MENSAJES ##########
    ############################################

    # Solicitamos una lista de los mensajes
    result = service.users().messages().list(userId='me').execute()

    # Esta variable es una lista de diccionarios donde cada uno contiene un message id
    messages = result.get('messages')

    ####################################################
    ########## RECORRO LOS MENSAJES OBTENIDOS ##########
    ####################################################

    # Itero usando messages
    for msg in messages:

        ###############################################################
        ########## OBTENGO PAYLOAD Y HEADERS DE CADA MENSAJE ##########
        ###############################################################

        # Obtengo todos los mensajes enviados al id y los guardo en txt
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()

        # Uso de try-except para evitar cualquier error
        try:
            # Dentro del diccionario txt guardo 'payload'
            payload = txt['payload']
            # Dentro de payload guardo 'headers'
            headers = payload['headers']

            ########################################################################
            ########## DEL HEADER OBTENGO Y GUARDO SUBJECT, SENDER Y DATE ##########
            ########################################################################

            # Busco Subject, Sender y Date dentro de headers
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']
                if d['name'] == 'Date':
                    date = d['value']

            ###################################################
            ########## ME CONECTO A LA BASE DE DATOS ##########
            ###################################################

            # Creo la conexion con la base de datos local
            mydb = mysql.connector.connect(
                host="localhost",
                user="mlsofia",
                password="MLsofia123$",
                database="mldatabase"
            )

            # Defino el cursor
            cursor = mydb.cursor()

            ######################################################
            ########## VALIDO LA ESTRUCTURA DEL PAYLOAD ##########
            ######################################################

            # Defino la estructura de los datos obtenidos ya que
            # varia si sender == receiver de sender != receiver

            # Valido que no contenga un objeto None
            if payload.get('parts') is not None:

                #####################################
                ########## OBTENGO EL BODY ##########
                #####################################

                # Guardo el contenido del primer atributo de parts
                parts = payload.get('parts')[0]
                # Busco dentro de parts 'body' y dentro de body 'data' y guardo el contenido
                data = parts['body']['data']
                # Formateo un poco data
                data = data.replace("-", "+").replace("_", "/")
                # El cuerpo del mensaje esta encriptado, hago un decode con base 64
                decoded_data = base64.b64decode(data)

                # Con los datos obtenidos en formato lxml, procedemos a parsearlo
                # con la libreria BeautifulSoup
                soup = BeautifulSoup(decoded_data, "lxml")
                # Obtengo el texto del mensaje con el metodo get_text()
                # y lo guardo en body para que sea mas claro
                body = soup.get_text()

                #############################################
                ########## BUSCO LA PALABRA DEVOPS ##########
                #############################################

                # Busco la palabra devops en el body y con el metodo lower()
                # paso todo el cuerpo a minusculas asi no tengo problemas en la busqueda
                if "devops" in body.lower():
                    # Creo la variable table para la validacion
                    table = "ml_devops_mail"
                    # Sentencia de MYSQL para ver las tablas creadas
                    cursor.execute("SHOW TABLES;")
                    # Guardo el output en result
                    result = cursor.fetchall()
                    # Paso a string el output
                    show_tables = [item[0] for item in result]

                    ##################################################################################
                    ########## VALIDO SI EXISTE LA TABLA E INSERTO EL REGISTRO SI NO EXISTE ##########
                    ##################################################################################

                    # Valido que la tabla que necesito este en el show table
                    # si no existe la creo y si existe hago el insert
                    if table in show_tables:
                        print("Table exist")

                        # Defino el comando
                        # sql = "INSERT INTO ml_devops_mail (sender, subject, date) VALUES (%s, %s, %s)"
                        sql = "INSERT INTO ml_devops_mail (sender, subject, date) SELECT * FROM (SELECT %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT sender, subject, date FROM ml_devops_mail WHERE sender = %s AND subject = %s AND date = %s) LIMIT 1;"
                        # Le paso los values
                        val = (sender, subject, date, sender, subject, date)
                        # Ejecuto el create table
                        cursor.execute(sql, val)
                        # Commiteo
                        mydb.commit()
                        # Cierro la conexion
                        cursor.close()
                        mydb.close()

                    else:
                        print("Table does not exist")
                        # Creo la tabla
                        cursor.execute("CREATE TABLE ml_devops_mail (id INT AUTO_INCREMENT UNIQUE PRIMARY KEY, sender VARCHAR(255), subject VARCHAR(255), date VARCHAR(255));")

                        # Defino el comando
                        # sql = "INSERT INTO ml_devops_mail (sender, subject, date) VALUES (%s, %s, %s)"
                        sql = "INSERT INTO ml_devops_mail (sender, subject, date) SELECT * FROM (SELECT %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT sender, subject, date FROM ml_devops_mail WHERE sender = %s AND subject = %s AND date = %s) LIMIT 1;"
                        # Le paso los values
                        val = (sender, subject, date, sender, subject, date)
                        # Ejecuto el create table
                        cursor.execute(sql, val)
                        # Commiteo
                        mydb.commit()
                        # Cierro la conexion
                        cursor.close()
                        mydb.close()

            elif payload.get('body') is not None:

                #####################################
                ########## OBTENGO EL BODY ##########
                #####################################

                # Busco en payload el atributo 'body' y lo guardo en parts
                parts = payload.get('body')
                # De body obtengo el valor del atributo data y lo guardo
                data = parts['data']
                # Formateo un poco data
                data = data.replace("-", "+").replace("_", "/")
                # El cuerpo del mensaje esta encriptado, hago un decode con base 64
                decoded_data = base64.b64decode(data)

                # Con los datos obtenidos en formato lxml, procedemos a parsearlo
                # con la libreria BeautifulSoup
                soup = BeautifulSoup(decoded_data, "lxml")
                # Obtengo el texto del mensaje con el metodo get_text()
                # y lo guardo en body para que sea mas claro
                body = soup.get_text()

                #############################################
                ########## BUSCO LA PALABRA DEVOPS ##########
                #############################################

                # Busco la palabra devops en el body y con el metodo lower()
                # paso todo el cuerpo a minusculas asi no tengo problemas en la busqueda
                if "devops" in body.lower():
                    # Creo la variable table para la validacion
                    table = "ml_devops_mail"
                    # Sentencia de MYSQL para ver las tablas creadas
                    cursor.execute("SHOW TABLES;")
                    # Guardo el output en result
                    result = cursor.fetchall()
                    # Paso a string el output
                    show_tables = [item[0] for item in result]

                    ##################################################################################
                    ########## VALIDO SI EXISTE LA TABLA E INSERTO EL REGISTRO SI NO EXISTE ##########
                    ##################################################################################

                    # Valido que la tabla que necesito este en el show table
                    # si no existe la creo y si existe hago el insert
                    if table in show_tables:
                        print("Table exist")

                        # Defino el comando
                        # sql = "INSERT INTO ml_devops_mail (sender, subject, date) VALUES (%s, %s, %s)"
                        sql = "INSERT INTO ml_devops_mail (sender, subject, date) SELECT * FROM (SELECT %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT sender, subject, date FROM ml_devops_mail WHERE sender = %s AND subject = %s AND date = %s) LIMIT 1;"
                        # Le paso los values
                        val = (sender, subject, date, sender, subject, date)
                        # Ejecuto el create table
                        cursor.execute(sql, val)
                        # Commiteo
                        mydb.commit()
                        # Cierro la conexion
                        cursor.close()
                        mydb.close()

                    else:
                        print("Table does not exist")
                        # Creo la tabla
                        cursor.execute("CREATE TABLE ml_devops_mail (id INT AUTO_INCREMENT UNIQUE PRIMARY KEY, sender VARCHAR(255), subject VARCHAR(255), date VARCHAR(255));")

                        # Defino el comando
                        # sql = "INSERT INTO ml_devops_mail (sender, subject, date) VALUES (%s, %s, %s)"
                        sql = "INSERT INTO ml_devops_mail (sender, subject, date) SELECT * FROM (SELECT %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT sender, subject, date FROM ml_devops_mail WHERE sender = %s AND subject = %s AND date = %s) LIMIT 1;"
                        # Le paso los values
                        val = (sender, subject, date, sender, subject, date)
                        # Ejecuto el create table
                        cursor.execute(sql, val)
                        # Commiteo
                        mydb.commit()
                        # Cierro la conexion
                        cursor.close()
                        mydb.close()
            else:
                print("Error, no concuerda la estructura del output con el match.")
        except:
            print("Hubo un error.")

if __name__ == '__main__':
    main()
