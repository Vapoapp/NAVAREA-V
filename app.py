from flask import Flask, jsonify, send_from_directory
import os, json
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

NAVY_PAGE = "https://www.marinha.mil.br/chm/dados-do-segnav-aviso-radio-nautico-tela/avisos-radio-nauticos-e-sar"
LOCAL_JSON_PATH = os.path.join("static", "alertas.json")

scraper = cloudscraper.create_scraper(browser={"browser": "firefox", "platform": "windows", "mobile": False})

def _find_latest_json_url():
    r = scraper.get(NAVY_PAGE, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        if a["href"].lower().endswith(".json"):
            url = a["href"]
            if not url.startswith("http"):
                url = "https://www.marinha.mil.br" + url
            return url
    raise RuntimeError("Link .json não encontrado na página da Marinha.")

def _download_raw_json():
    json_url = _find_latest_json_url()
    r = scraper.get(json_url, timeout=40)
    r.raise_for_status()
    return r.json()

def _transform(raw):
    alertas = []
    for feat in raw.get("features", []):
        props = feat.get("properties", {}) or {}
        geom = feat.get("geometry", {}) or {}
        coords = geom.get("coordinates")
        alerta = {
            "numero": props.get("numero"),
            "texto": props.get("textoPT") or props.get("texto"),
            "tipo": props.get("tipo") or props.get("Tipo") or "",
            "pontos": None,
            "centro": None,
        }
        gtype = (geom.get("type") or "").lower()
        if gtype == "polygon" and coords:
            ring = coords[0]
            alerta["pontos"] = [[float(y), float(x)] for x, y in ring]
        elif gtype == "linestring" and coords:
            alerta["pontos"] = [[float(y), float(x)] for x, y in coords]
        elif gtype == "point" and coords:
            alerta["centro"] = [float(coords[1]), float(coords[0])]
        alertas.append(alerta)
    return alertas

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/alertas")
def alertas():
    try:
        raw = _download_raw_json()
        return jsonify(_transform(raw))
    except Exception as e:
        if os.path.exists(LOCAL_JSON_PATH):
            with open(LOCAL_JSON_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return jsonify(_transform(raw))
        return jsonify({"erro": str(e)}), 500

@app.route("/alertas_raw")
def alertas_raw():
    raw = _download_raw_json()
    return jsonify(raw)

@app.route("/baixar-json")
def baixar_json():
    raw = _download_raw_json()
    os.makedirs(os.path.dirname(LOCAL_JSON_PATH), exist_ok=True)
    with open(LOCAL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False)
    qtd = len(raw.get("features", []))
    return jsonify({"salvo_em": "/" + LOCAL_JSON_PATH.replace("\", "/"), "features": qtd})

@app.route("/static/<path:filename>")
def servir_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
