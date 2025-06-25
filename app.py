
from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)
STATIC_JSON_PATH = os.path.join('static', 'navarea.json')

def get_latest_json_url():
    base = "https://www.marinha.mil.br"
    page = base + "/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar"
    try:
        res = requests.get(page, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        link = soup.find("a", href=lambda href: href and "avradio_" in href and href.endswith(".json"))
        return base + link["href"] if link else None
    except Exception as e:
        print("Erro ao buscar URL mais recente:", e)
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alertas")
def alertas():
    try:
        with open(STATIC_JSON_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return jsonify(dados if isinstance(dados, list) else [])
    except:
        return jsonify([])

@app.route("/atualizar")
def atualizar():
    try:
        url = get_latest_json_url()
        if not url:
            raise Exception("URL JSON não encontrada")

        r = requests.get(url, timeout=10)
        dados = r.json()

        with open(STATIC_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        print(f"✔ Atualizado com sucesso de {url}")
        return jsonify({"status": "ok", "count": len(dados)})
    except Exception as e:
        print("Erro ao atualizar alertas:", e)
        return jsonify({"status": "erro", "mensagem": str(e)})
