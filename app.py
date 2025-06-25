from flask import Flask, render_template, jsonify
import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alertas")
def alertas():
    try:
        with open("static/navarea.json", "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route("/atualizar")
def atualizar():
    try:
        url_base = "https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar"
        response = requests.get(url_base, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        link_tag = soup.find("a", href=re.compile(r".*\.json$"))
        if not link_tag:
            return jsonify({"mensagem": "Erro: Nenhum arquivo JSON encontrado", "atualizacao": "Não disponível", "arquivo": "Desconhecido"})
        json_url = "https://www.marinha.mil.br" + link_tag["href"]
        nome_arquivo = json_url.split("/")[-1]

        dados = requests.get(json_url, timeout=10).json()
        with open("static/navarea.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        return jsonify({
            "mensagem": f"Atualizado com sucesso. {len(dados)} alertas carregados.",
            "atualizacao": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "arquivo": nome_arquivo
        })
    except Exception as e:
        return jsonify({"mensagem": "Erro ao atualizar", "erro": str(e), "atualizacao": "Não disponível", "arquivo": "Desconhecido"})