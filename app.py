from flask import Flask, render_template, jsonify
import requests
import json
import os
from bs4 import BeautifulSoup

app = Flask(__name__)
DATA_PATH = os.path.join("static", "navarea.json")

def buscar_json_mais_recente():
    url_base = "https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar"
    try:
        r = requests.get(url_base, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        link_json = soup.find("a", href=lambda href: href and href.endswith(".json"))
        if link_json:
            url_json = link_json["href"]
            if not url_json.startswith("http"):
                url_json = "https://www.marinha.mil.br" + url_json
            r_json = requests.get(url_json, timeout=10)
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                f.write(r_json.text)
    except Exception as e:
        print(f"Erro ao buscar JSON: {e}")

@app.route("/")
def index():
    buscar_json_mais_recente()
    return render_template("index.html")

@app.route("/alertas")
def alertas():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route("/atualizar")
def atualizar():
    buscar_json_mais_recente()
    return jsonify({"status": "ok"})
