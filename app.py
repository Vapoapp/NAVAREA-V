
from flask import Flask, render_template, jsonify
import requests
import os
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import traceback

app = Flask(__name__)
DATA_FOLDER = 'static'
LOCAL_JSON = os.path.join(DATA_FOLDER, 'navarea.json')
UPDATE_LOG = os.path.join(DATA_FOLDER, 'ultima_atualizacao.txt')

def parse_geometry(alerta):
    geometry = alerta.get("geometry", "")
    texto = alerta.get("textoPT", "") or alerta.get("texto", "")
    resultado = {
        "numero": alerta.get("numero", ""),
        "texto": texto.strip()
    }

    # Extrair coordenadas de geometry
    matches = re.findall(r'LatLng\((-?\d+\.\d+),\s*(-?\d+\.\d+)\)', geometry)
    coords = [[float(lat), float(lon)] for lat, lon in matches]

    if "Polygon" in geometry or ("AREA LIMITADA" in texto.upper() and len(coords) >= 3):
        resultado["pontos"] = coords
    elif "Polyline" in geometry or ("ENTRE" in texto.upper() and len(coords) == 2):
        resultado["pontos"] = coords
    elif coords:
        resultado["centro"] = coords[0]

    return resultado

def baixar_json_mais_recente():
    url_base = "https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar"
    try:
        res = requests.get(url_base, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        link = soup.find('a', href=True, string=lambda s: s and s.endswith('.json'))
        if not link:
            print("Nenhum link .json encontrado na página.")
            return False
        json_url = "https://www.marinha.mil.br" + link['href']
        print("Baixando JSON:", json_url)
        json_data = requests.get(json_url, timeout=10).json()

        dados = json_data.get("avisos", [])  # lista de alertas
        os.makedirs(DATA_FOLDER, exist_ok=True)
        with open(LOCAL_JSON, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        with open(UPDATE_LOG, 'w', encoding='utf-8') as f:
            f.write(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        return True
    except Exception as e:
        print("Erro ao baixar JSON:", e)
        traceback.print_exc()
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    if not os.path.exists(LOCAL_JSON):
        baixar_json_mais_recente()
    try:
        with open(LOCAL_JSON, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            processados = [parse_geometry(a) for a in dados]
            return jsonify(processados)
    except Exception as e:
        print("Erro ao carregar alertas:", e)
        traceback.print_exc()
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    sucesso = baixar_json_mais_recente()
    if not sucesso:
        return jsonify([])

    try:
        with open(LOCAL_JSON, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            processados = [parse_geometry(a) for a in dados]
            return jsonify(processados)
    except Exception as e:
        print("Erro ao atualizar:", e)
        traceback.print_exc()
        return jsonify([])

@app.route('/ultima-atualizacao')
def ultima_atualizacao():
    if os.path.exists(UPDATE_LOG):
        with open(UPDATE_LOG, 'r', encoding='utf-8') as f:
            return f.read()
    return "Não disponível"
