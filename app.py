
from flask import Flask, render_template, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alertas')
def alertas():
    try:
        with open('static/navarea.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except:
        dados = []

    alertas_processados = []
    for alerta in dados:
        geometry = alerta.get('geometry', {})
        tipo_geom = geometry.get('type')
        coordenadas = geometry.get('coordinates')
        numero = alerta.get('numero', '').upper()

        # Detectar se é alerta SAR com base no campo 'numero'
        if 'SAR' in numero:
            icon = 'static/sar-icon.png'
        else:
            icon = 'static/plataforma-icon.png'

        alerta_processado = {
            'titulo': alerta.get('titulo', ''),
            'mensagem': alerta.get('mensagem', ''),
            'geometry': geometry,
            'icone': icon
        }
        alertas_processados.append(alerta_processado)

    return jsonify(alertas_processados)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
