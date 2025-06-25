
from flask import Flask, render_template, jsonify
import requests
import json
import os
from bs4 import BeautifulSoup

app = Flask(__name__)
DATA_PATH = 'static/navarea.json'

def baixar_json_recente():
    try:
        url_pagina = 'https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar'
        resposta = requests.get(url_pagina, timeout=10)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        links = soup.find_all('a', href=True)
        json_links = [a['href'] for a in links if a['href'].endswith('.json')]
        if json_links:
            url_json = json_links[0]
            if not url_json.startswith('http'):
                url_json = 'https://www.marinha.mil.br' + url_json
            json_data = requests.get(url_json, timeout=10).json()
            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print('✅ Arquivo JSON atualizado com sucesso.')
        else:
            print('⚠️ Nenhum arquivo JSON encontrado.')
    except Exception as e:
        print(f'Erro ao baixar JSON: {e}')

@app.route("/")
def index():
    baixar_json_recente()
    return render_template("index.html")

@app.route("/alertas")
def alertas():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])
