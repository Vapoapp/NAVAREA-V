
from flask import Flask, jsonify, render_template
import json
import re

app = Flask(__name__)
DATA_PATH = 'navarea.json'

def parse_geometry(alerta):
    geometry = alerta.get("geometry", "")
    texto = alerta.get("textoPT", "")
    resultado = {
        "numero": alerta.get("numero", ""),
        "texto": texto.strip()
    }

    # Extrair coordenadas do geometry se existir
    matches = re.findall(r'LatLng\((-?\d+\.\d+),\s*(-?\d+\.\d+)\)', geometry)
    coords = [[float(lat), float(lon)] for lat, lon in matches]

    if "Polygon" in geometry or ("AREA LIMITADA" in texto.upper() and len(coords) >= 3):
        resultado["pontos"] = coords
    elif "Polyline" in geometry or ("ENTRE" in texto.upper() and len(coords) == 2):
        resultado["pontos"] = coords
    elif coords:
        resultado["centro"] = coords[0]

    return resultado

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            processados = [parse_geometry(alerta) for alerta in dados]
            return jsonify(processados)
    except Exception as e:
        print("Erro ao carregar alertas:", e)
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    try:
        import requests
        url = 'https://www.marinha.mil.br/chm/sites/www.marinha.mil.br.chm/files/opt/avradio_318.json'
        r = requests.get(url, timeout=10)
        dados = r.json().get("avisos", [])
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        processados = [parse_geometry(alerta) for alerta in dados]
        return jsonify(processados)
    except Exception as e:
        print("Erro ao atualizar:", e)
        return jsonify([])
