from flask import Flask, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
import re, json

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/alertas')
def get_alertas():
    try:
        url_base = "https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar"
        response = requests.get(url_base, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        link_json = None
        for a in soup.find_all('a', href=True):
            if a['href'].endswith('.json'):
                link_json = a['href']
                break

        if not link_json:
            return jsonify({"erro": "Nenhum arquivo JSON encontrado"}), 404

        if not link_json.startswith("http"):
            link_json = "https://www.marinha.mil.br" + link_json

        data = requests.get(link_json, timeout=20).json()
        alertas = []

        for a in data.get("features", []):
            props = a.get("properties", {})
            geom = a.get("geometry", {})
            tipo = props.get("tipo", "")
            coords = geom.get("coordinates")

            alerta = {
                "numero": props.get("numero"),
                "texto": props.get("textoPT") or props.get("texto"),
                "tipo": tipo,
                "pontos": None,
                "centro": None
            }

            if geom.get("type") == "Polygon":
                alerta["pontos"] = [[float(y), float(x)] for x, y in geom["coordinates"][0]]
            elif geom.get("type") == "LineString":
                alerta["pontos"] = [[float(y), float(x)] for x, y in coords]
            elif geom.get("type") == "Point":
                alerta["centro"] = [float(coords[1]), float(coords[0])]

            alertas.append(alerta)

        print(f"✅ {len(alertas)} alertas carregados.")
        return jsonify(alertas)

    except Exception as e:
        print(f"⚠️ Erro ao buscar alertas: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route('/atualizar')
def atualizar_alertas():
    return get_alertas()

@app.route('/static/<path:filename>')
def servir_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
