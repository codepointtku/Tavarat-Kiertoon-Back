import glob
import os

key = os.getenv("SSL_KEY", "./ssl/*.key")
cert = os.getenv("SSL_CRT", "./ssl/*.crt")

certfile = glob.glob(cert)[0]

keyfile = glob.glob(key)[0]

print(certfile)
print(keyfile)

bind = os.getenv("WEB_BIND", "0.0.0.0:8000")
reload = os.getenv("WEB_RELOAD", "false")
