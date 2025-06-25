
from flask import Flask, render_template, jsonify
import requests
import json
import os
import re
from bs4 import BeautifulSoup

app = Flask(__name__)
DATA_PATH = 'static/navarea.json'
os.makedirs('static', exist_ok=True)

def extrair_coordenadas(texto):
    padrao = r"(\d{1,2})°\s?(\d{1,2})['"]?\s?(\d{1,2})?['"]?[ ]*([NS])[, ]+\s*(\d{1,3})°\s?(\d{1,2})['"]?\s?(\d{1,2})?['"]?[ ]*([WO])"
    encontrados = []
    for match in re.finditer(padrao, texto):
        lat_g, lat_m, lat_s, lat_dir, lon_g, lon_m, lon_s, lon_dir = match.groups()
        lat = int(lat_g) + int(lat_m)/60 + (int(lat_s) if lat_s else 0)/3600
        lon = int(lon_g) + int(lon_m)/60 + (int(lon_s) if lon_s else 0)/3600
        if lat_dir == 'S': lat *= -1
        if lon_dir == 'W': lon *= -1
        encontrados.append([lat, lon])
    return encontrados

def extrair_alertas(conteudo_json):
    alertas = []
    for item in conteudo_json.get('features', []):
        props = item.get('properties', {})
        geometry = item.get('geometry', {})
        texto = props.get('message', '')
        coords_extraidas = extrair_coordenadas(texto)
        tipo_geom = geometry.get('type')
        coords_geom = geometry.get('coordinates')

        if tipo_geom == 'Point':
            alerta = {'tipo': 'Point', 'coordenadas': coords_geom[::-1], 'mensagem': texto}
        elif tipo_geom in ['Polygon', 'LineString']:
            alerta = {'tipo': tipo_geom, 'coordenadas': coords_geom, 'mensagem': texto}
        elif coords_extraidas:
            for coord in coords_extraidas:
                alertas.append({'tipo': 'Point', 'coordenadas': coord, 'mensagem': texto})
            continue
        else:
            continue
        alertas.append(alerta)
    return alertas

def baixar_json_mais_recente():
    url_base = "https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar"
    try:
        r = requests.get(url_base, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        link = soup.find('a', href=True, string=re.compile(r"\.json$"))
        if link:
            href = link['href']
            if not href.startswith("http"):
                href = "https://www.marinha.mil.br" + href
            return href
    except Exception as e:
        print("Erro ao localizar JSON:", e)
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alertas")
def alertas():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
            return jsonify(data)
    except Exception as e:
        print("Erro ao carregar alertas:", e)
        return jsonify([])

@app.route("/atualizar")
def atualizar():
    try:
        url = baixar_json_mais_recente()
        if not url:
            print("⚠️  Nenhum link .json encontrado.")
            return "Erro ao localizar link", 500

        print("🔄 Baixando de", url)
        r = requests.get(url, timeout=10)
        dados = json.loads(r.text)

        alertas_extraidos = extrair_alertas(dados)
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(alertas_extraidos, f, ensure_ascii=False, indent=2)

        print("✅ Atualização concluída.")
        return "Atualização concluída."
    except Exception as e:
        print("❌ Erro durante atualização:", e)
        return "Erro interno", 500
