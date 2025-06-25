
from flask import Flask, render_template, jsonify
import requests
import json

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
        try:
            dados = r.json()
        except Exception as e:
            print("[ERRO] JSON inválido:", r.text[:300])
            raise
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Alertas atualizados. Total: {len(dados)}")
        return jsonify(dados)
    except Exception as e:
        print("[ERRO] Falha ao atualizar alertas:", str(e))
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except:
            return jsonify([])

@app.route('/atualizar')
def atualizar():
    return alertas()
