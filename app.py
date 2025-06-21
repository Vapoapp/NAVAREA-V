from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

app = Flask(__name__)

DATA_PATH = "navarea.json"

def simular_coordenadas(index):
    base_lat = -23.0
    base_lon = -42.6
    shift = 0.1 * index
    return [
        [base_lat - shift, base_lon - shift],
        [base_lat - shift, base_lon + shift],
        [base_lat + shift, base_lon + shift],
        [base_lat + shift, base_lon - shift]
    ]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alertas")
def alertas():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except:
        return jsonify([])

@app.route("/atualizar")
def atualizar():
    url = "https://www.marinha.mil.br/chm/dados-do-segnav/avisos-navarea"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        itens = soup.select(".field__item")

        alertas = []
        for i, item in enumerate(itens[:5]):
            texto = item.get_text(strip=True, separator=" ")
            titulo = f"NAVAREA V {i+1:03}/2024"
            descricao = texto[:200] + "..." if len(texto) > 200 else texto
            poligono = simular_coordenadas(i)
            centro = [sum(p[0] for p in poligono)/4, sum(p[1] for p in poligono)/4]
            alerta = {
                "titulo": titulo,
                "descricao": descricao,
                "data": datetime.now().isoformat(),
                "centro": centro,
                "cor": "#cc0000",
                "poligono": poligono
            }
            alertas.append(alerta)

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(alertas, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "ok", "total": len(alertas)})

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
