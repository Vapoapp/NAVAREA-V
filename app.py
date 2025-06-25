
from flask import Flask, render_template, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)
DATA_PATH = 'static/navarea.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        url = 'https://www.marinha.mil.br/chm/sites/www.marinha.mil.br.chm/files/opt/avradio_318.json'
        r = requests.get(url, timeout=10)
        dados = r.json()
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return jsonify(dados)
    except Exception as e:
        print("Erro ao atualizar alertas:", e)
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except:
            return jsonify([])
