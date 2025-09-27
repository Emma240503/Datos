import requests
import json
import os

# URLs de la API
URL_MAPA = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map"
URL_PEDIDOS = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs"
URL_CLIMA = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather"


LOCAL_MAPA = "data/ciudad.json"
LOCAL_PEDIDOS = "data/pedidos.json"
LOCAL_CLIMA = "data/clima.json"

def obtener_mapa():
    try:
        resp = requests.get(URL_MAPA, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except:
        print(" No se pudo conectar a la API. Usando mapa local...")
    with open(LOCAL_MAPA, "r") as f:
        return json.load(f)

def obtener_pedidos():
    try:
        resp = requests.get(URL_PEDIDOS, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except:
        print(" No se pudo conectar a la API. Usando pedidos locales...")
    with open(LOCAL_PEDIDOS, "r") as f:
        return json.load(f)

def obtener_clima():
    try:
        resp = requests.get(URL_CLIMA, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except:
        print(" No se pudo conectar a la API. Usando clima local...")
    with open(LOCAL_CLIMA, "r") as f:
        return json.load(f)
