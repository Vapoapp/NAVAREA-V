
from flask import Flask, render_template, jsonify
import requests
import json
import os

app = Flask(__name__)

# Caminho para o JSON de alertas
DATA_PATH = 'static/navarea.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Adiciona ícone personalizado para SAR com geometry == Point
        for alerta in dados:
            if (
                alerta.get("tipo") == "SAR"
                and isinstance(alerta.get("geometry"), dict)
                and alerta["geometry"].get("type") == "Point"
            ):
                alerta["icon"] = "static/sar-icon.png"

        return jsonify(dados)

    except Exception as e:
        print("Erro ao carregar alertas:", e)
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    url_base = "https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar"
    try:
        r = requests.get(url_base, timeout=10)
        r.raise_for_status()

        # Extrai nome do arquivo .json mais recente
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        link_json = soup.find('a', href=True, string=lambda t: t and t.endswith('.json'))

        if not link_json:
            raise Exception("Arquivo .json não encontrado no site da Marinha.")

        json_url = "https://www.marinha.mil.br" + link_json['href']
        r_json = requests.get(json_url)
        r_json.raise_for_status()

        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            f.write(r_json.text)

        return jsonify({"mensagem": "Alertas atualizados com sucesso."})

    except Exception as e:
        print("Erro ao atualizar:", e)
        return jsonify({"erro": str(e)})
