
from flask import Flask, render_template, jsonify
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)
DATA_PATH = 'static/navarea.json'

def parse_geometry(alerta):
    geometry = alerta.get("geometry", "")
    texto = alerta.get("textoPT", "") or alerta.get("texto", "")
    matches = re.findall(r'LatLng\\((-?\\d+\\.\\d+),\\s*(-?\\d+\\.\\d+)\\)', geometry)
    coords = [[float(lat), float(lon)] for lat, lon in matches]
    if "Polygon" in geometry or ("AREA LIMITADA" in texto.upper() and len(coords) >= 3):
        return {
            "tipo": "poligono",
            "coordenadas": coords,
            "texto": texto
        }
    elif "Polyline" in geometry or ("ENTRE" in texto.upper() and len(coords) == 2):
        return {
            "tipo": "linha",
            "coordenadas": coords,
            "texto": texto
        }
    elif coords:
        return {
            "tipo": "ponto",
            "coordenadas": coords[0],
            "texto": texto
        }
    else:
        return {
            "tipo": "desconhecido",
            "coordenadas": [],
            "texto": texto
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            processados = [parse_geometry(alerta) for alerta in dados if isinstance(alerta, dict)]
            return jsonify(processados)
    except Exception as e:
        print("Erro ao carregar alertas:", e)
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    try:
        url_base = 'https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar'
        pagina = requests.get(url_base, timeout=10)
        links = re.findall(r'href="([^"]+\\.json)"', pagina.text)
        link_json = next((l for l in links if l.endswith('.json')), None)
        if not link_json:
            raise Exception("JSON não encontrado.")
        if not link_json.startswith('http'):
            link_json = 'https://www.marinha.mil.br' + link_json
        print(f"Baixando de {link_json}")
        dados = requests.get(link_json, timeout=10).json()
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print("Atualização concluída.")
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Erro:", e)
        return jsonify({"status": "erro", "mensagem": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
