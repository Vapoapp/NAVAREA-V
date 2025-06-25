from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import json
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open('static/navarea.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    url_site = 'https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar'
    try:
        response = requests.get(url_site, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        link = soup.find('a', href=re.compile(r'\.json$'))
        if not link:
            return 'Erro: Arquivo .json não encontrado no site da Marinha.', 500
        json_url = link['href']
        if not json_url.startswith('http'):
            json_url = f'https://www.marinha.mil.br{json_url}'
        print(f"Baixando de {json_url}")
        dados = requests.get(json_url, timeout=10).json()
        with open('static/navarea.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print("Atualização concluída.")
        return 'Atualização concluída.'
    except Exception as e:
        print('Erro ao atualizar:', e)
        return 'Erro ao atualizar', 500
