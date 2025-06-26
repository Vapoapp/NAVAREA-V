
from flask import Flask, render_template, jsonify
import requests
import json
import os
from datetime import datetime
from urllib.parse import urljoin

app = Flask(__name__)
STATIC_FOLDER = 'static'
DATA_PATH = os.path.join(STATIC_FOLDER, 'navarea.json')
MARINHA_URL = 'https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar'

def baixar_json_mais_recente():
    try:
        html = requests.get(MARINHA_URL, timeout=10).text
        for linha in html.split('"'):
            if linha.endswith('.json') and 'avradio_' in linha:
                json_url = urljoin(MARINHA_URL, linha)
                break
        else:
            return False, 'Arquivo .json não encontrado na página da Marinha.'

        r = requests.get(json_url, timeout=15)
        if r.status_code == 200:
            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                f.write(r.text)
            return True, f'Atualizado com sucesso em {datetime.now().strftime("%d/%m/%Y %H:%M")}'
        return False, 'Erro ao baixar JSON.'
    except Exception as e:
        return False, f'Erro: {e}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        processados = []
        for alerta in dados:
            geometria = alerta.get('geometry')
            tipo = 'navarea'
            nome = alerta.get('nome', '').upper()
            if 'SAR' in nome or nome.startswith('ALERTA SAR'):
                tipo = 'sar'

            processados.append({
                'nome': nome,
                'descricao': alerta.get('descricao', ''),
                'geometry': geometria,
                'tipo': tipo
            })
        return jsonify(processados)
    except Exception as e:
        return jsonify([])

@app.route('/atualizar')
def atualizar():
    sucesso, mensagem = baixar_json_mais_recente()
    return jsonify({'mensagem': mensagem, 'sucesso': sucesso})

if __name__ == '__main__':
    app.run(debug=True)
