
from flask import Flask, render_template, jsonify
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)
JSON_PATH = 'static/navarea.json'

def extrair_coordenadas(texto):
    padrao = r"(\d{1,2})°\s?(\d{1,2})[′']?\s?(\d{1,2})?[″\"]?\s*([NS])[, ]+\s*(\d{1,3})°\s?(\d{1,2})[′']?\s?(\d{1,2})?[″\"]?\s*([WO])"
    encontrados = re.findall(padrao, texto)
    coordenadas = []
    for lat_g, lat_m, lat_s, lat_dir, lon_g, lon_m, lon_s, lon_dir in encontrados:
        lat = int(lat_g) + int(lat_m)/60 + (int(lat_s)/3600 if lat_s else 0)
        lon = int(lon_g) + int(lon_m)/60 + (int(lon_s)/3600 if lon_s else 0)
        if lat_dir == 'S': lat *= -1
        if lon_dir == 'W': lon *= -1
        coordenadas.append([lat, lon])
    return coordenadas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    try:
        url_base = 'https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar'
        pagina = requests.get(url_base, timeout=10)
        links = re.findall(r'href="([^"]+\.json)"', pagina.text)
        link_json = next((l for l in links if l.endswith('.json')), None)
        if not link_json:
            raise Exception("JSON não encontrado.")
        if not link_json.startswith('http'):
            link_json = 'https://www.marinha.mil.br' + link_json
        print(f"Baixando de {link_json}")
        dados = requests.get(link_json, timeout=10).json()
        for alerta in dados:
            if 'geometry' not in alerta or not alerta['geometry']:
                coords_extraidas = extrair_coordenadas(alerta.get('texto', ''))
                if coords_extraidas:
                    alerta['geometry'] = {
                        'type': 'Point',
                        'coordinates': coords_extraidas[0]
                    }
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print("Atualização concluída.")
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Erro:", e)
        return jsonify({"status": "erro", "mensagem": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
