# ML-GMAIL-API

Programa de python el cual realiza lo siguiente:

* Conectarse a la API de gmail.
* Capturar todos los mails.
* Obtener el cuerpo del mail encodeado en base 64 y desencodearlo.
* Buscar dentro del cuerpo del mail por la plabara `devops`.
* Guardar, de los mails que hagan match, `seder, subject y date`
* Envia los datos guardados a una base de datos de MySQL en un contenedor de Docker corriendo local.

> Nota: Si la base de datos no existe la crea y si el registro que va a insertar ya existe lo ignora.

## Requesitos para ejecutar el programa

* Cuenta de Gmail
* Configurar Gmail API para poder autenticarse (Ver:[Quickstart](https://developers.google.com/gmail/api/quickstart/python).).
* Git (Ver: [Git Download](https://git-scm.com/downloads).
* Docker (Ver: [Install Docker Engine]("https://docs.docker.com/engine/install/)).
* Python3 (Ver: [Python Download](https://www.python.org/downloads/)).
* PIP (Ver: [PIP](https://pip.pypa.io/en/stable/installation/).)
* Paquetes PIP necesarios: 

`  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib pickle-mixin bs4 mysql-connector-python`

## Pasos:

* Clonar repositorio: 

`git clone https://github.com/sofia008/ml-gmail-api.git`

* Crear contenedor MySQL Docker:

`docker run -p 3306:3306 --name ml-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -e MYSQL_DATABASE=mldatabase -e MYSQL_USER=mlsofia -e MYSQL_PASSWORD=MLsofia123$ -d mysql`

> Nota: Para conectarse a la base de datos: `mysql -h localhost --protocol=tcp -u mlsofia -pMLsofia123$ mldatabase`

* El archivo `credentials.json` obtenido de [Python Gmail Api Quickstart](https://developers.google.com/gmail/api/quickstart/python) ubicarlo en el root del repositorio.

* En el root del repositorio ejecutar:

`python3 quickstart.py`


## Sitios consultados:

* [Python Gmail Api Quickstart](https://developers.google.com/gmail/api/quickstart/python).
* [How to read Emails from Gmail using Gmail API in Python ?](https://www.geeksforgeeks.org/how-to-read-emails-from-gmail-using-gmail-api-in-python/).