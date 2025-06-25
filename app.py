
from flask import Flask, render_template, jsonify
import requests
import json
import re
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
DATA_PATH = 'static/navarea.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        print("Erro ao carregar navarea.json:", e)
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    try:
        url_base = 'https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar'
        html = requests.get(url_base, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')
        link = soup.find('a', href=re.compile(r'\.json$'))
        if not link:
            print("❌ Nenhum link JSON encontrado.")
            return jsonify({'erro': 'Arquivo .json não encontrado na página da Marinha'}), 500
        url_json = link['href']
        if not url_json.startswith('http'):
            url_json = 'https://www.marinha.mil.br' + url_json
        print("🔗 Baixando de:", url_json)
        r = requests.get(url_json, timeout=10)
        dados = r.json()
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print("✅ Atualização concluída.")
        return jsonify({'mensagem': 'Atualização concluída'})
    except Exception as e:
        print("Erro ao atualizar:", e)
        return jsonify({'erro': 'Falha ao atualizar os dados'}), 500
