from flask import Flask, render_template, jsonify, request
import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from geopy.distance import geodesic

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


def distancia_ponto_segmento(ponto, segmento):
    """Calcula a menor distância entre um ponto e um segmento da rota."""
    return min(geodesic(ponto, segmento[0]).nautical, geodesic(ponto, segmento[1]).nautical)

@app.route("/filtrar_alertas", methods=["POST"])
def filtrar_alertas():
    data = request.json
    rota = data.get("rota", [])
    distancia_limite = 5

    try:
        with open("static/navarea.json", "r", encoding="utf-8") as f:
            alertas = json.load(f)
    except:
        return jsonify([])

    exportar = []
    codigos_vistos = set()

    for alerta in alertas:
        numero = alerta.get("numero", "")
        if numero in codigos_vistos:
            continue

        coords = alerta.get("coordenadas", [])
        if not coords or not rota:
            continue

        for ponto in coords:
            for i in range(len(rota) - 1):
                segmento = [rota[i], rota[i + 1]]
                if distancia_ponto_segmento(ponto, segmento) <= distancia_limite:
                    exportar.append(alerta)
                    codigos_vistos.add(numero)
                    break
            else:
                continue
            break

    return jsonify(exportar)