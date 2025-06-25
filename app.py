
from flask import Flask, render_template, jsonify
import requests
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)
DATA_FOLDER = 'static'
LOCAL_JSON = os.path.join(DATA_FOLDER, 'navarea.json')
UPDATE_LOG = os.path.join(DATA_FOLDER, 'ultima_atualizacao.txt')

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
        json_data = requests.get(json_url, timeout=10).json()
        os.makedirs(DATA_FOLDER, exist_ok=True)
        with open(LOCAL_JSON, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        with open(UPDATE_LOG, 'w', encoding='utf-8') as f:
            f.write(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        return True
    except Exception as e:
        print("Erro ao baixar JSON:", e)
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
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    sucesso = baixar_json_mais_recente()
    if not sucesso:
        return jsonify([])

    try:
        with open(LOCAL_JSON, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route('/ultima-atualizacao')
def ultima_atualizacao():
    if os.path.exists(UPDATE_LOG):
        with open(UPDATE_LOG, 'r', encoding='utf-8') as f:
            return f.read()
    return "Não disponível"
