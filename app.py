
from flask import Flask, render_template, jsonify, send_from_directory
import requests
import json
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open('static/navarea.json', 'r', encoding='utf-8') as f:
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
        link = soup.find('a', href=re.compile(r'.*\.json$'))
        if not link:
            return jsonify({'erro': 'JSON não encontrado'})
        url_json = link['href']
        if not url_json.startswith('http'):
            url_json = 'https://www.marinha.mil.br' + url_json
        r = requests.get(url_json, timeout=10)
        with open('static/navarea.json', 'w', encoding='utf-8') as f:
            f.write(r.text)
        return jsonify({'mensagem': 'Atualização concluída.'})
    except Exception as e:
        print("Erro ao atualizar:", e)
        return jsonify({'erro': 'Erro ao atualizar os dados.'})
