import glob
import os
import datetime

key = os.getenv("SSL_KEY", "./ssl/*.key")
cert = os.getenv("SSL_CRT", "./ssl/*.crt")

certfile = glob.glob(cert)[0]
keyfile = glob.glob(key)[0]

bind = os.getenv("WEB_BIND", "0.0.0.0:8000")
reload = os.getenv("WEB_RELOAD", "false")
now = datetime.datetime.now().strftime("%m-%Y")
log_location = os.getenv("LOG_LOCATION", "/logs")
accesslog = f"{log_location}/tk-access-{now}.log"
errorlog = f"{log_location}/tk-error-{now}.log"
loglevel = "warning"
