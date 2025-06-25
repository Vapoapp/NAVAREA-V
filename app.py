
from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import re
import json
import os

app = Flask(__name__)
STATIC_JSON = 'static/navarea.json'

def baixar_alertas():
    try:
        url_pagina = 'https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar'
        html = requests.get(url_pagina, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')

        link_tag = soup.find('a', href=re.compile(r'avradio_\d+\.json$'))
        if not link_tag:
            print("⚠️ Nenhum JSON encontrado na página da Marinha.")
            return False

        json_url = 'https://www.marinha.mil.br' + link_tag['href']
        response = requests.get(json_url, timeout=10)

        if response.status_code != 200:
            print(f"⚠️ Erro ao baixar JSON: {response.status_code}")
            return False

        dados = response.json()
        with open(STATIC_JSON, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print("✅ Alertas NAVAREA atualizados com sucesso.")
        return True

    except Exception as e:
        print(f"Erro ao atualizar alertas: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    if not os.path.exists(STATIC_JSON):
        return jsonify([])

    try:
        with open(STATIC_JSON, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        print(f"Erro ao ler alertas: {e}")
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    sucesso = baixar_alertas()
    return jsonify({'ok': sucesso})

if __name__ == '__main__':
    app.run(debug=True)
