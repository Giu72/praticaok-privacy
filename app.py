import os
import time
import base64
from difflib import SequenceMatcher
from flask import Flask, request, jsonify
from pyairtable import Api
import requests as req

app = Flask(__name__)

# ─── CONFIGURAZIONE ───────────────────────────────────────────────────────────
AIRTABLE_TOKEN = "pat5R6Hzz11DFLqkx.37639cb89ca2562dbeca7f837f576c2e916e135eb94712f9ca4d4bc1d7b826f3"
BASE_ID = "app9mXSzgqGOhYtpd"
TABLE_NAME = "Clienti"
VERIFY_TOKEN = "praticaok2024"

META_TOKEN = "EAA8G41qOXgUBRZAdyldEJguRRIO7Lbdi8ujyB3BT2vHWcpcDBAqnCCNUu8sv7YMTAa473al52T5B78U8MZCZASdt5FwaMGZBemglb9rnqJZCmYakWfsQ1Y7rGXv62FZArSDD9TEqoNZBhZAxYBnUIU278GIReLLgbbwyW4rHXsYr4VacQZCEvPe6f0yHISueP8p7Gy5vLnIeUmkEGPUHt4VzvQDHVnZAojScZAsObDQO0F0EZAuvEkhfhFPJfRwShLmXuVIFGL8B1e2ABcMrCcW8NlahBT7T"
PHONE_NUMBER_ID = "1156459807541320"

TELEGRAM_TOKEN = "8555023720:AAEpTP9E9EhfpQBra2oSQCIeaeNYdxapv2I"
TELEGRAM_CHANNEL_ID = "-1003939688675"

SINONIMI = {
    "CU": ["cu", "certificazione unica", "busta paga", "redditi", "lavoro"],
    "F24": ["f24", "modello f24", "pagamento", "tributi"],
    "Documento identità": ["documento identità", "carta identità", "carta d'identità", "patente", "passaporto", "identità"],
    "Codice fiscale": ["codice fiscale", "codici fiscale", "cf", "tessera sanitaria", "codfiscale", "cod fiscale"],
    "Buste paga ultime 3": ["busta paga", "buste paga", "cedolino", "stipendio", "buste paghe"],
    "CUD": ["cud", "modello cud"],
    "Estratto conto 6 mesi": ["estratto conto", "conto corrente", "movimenti", "estrato conto"],
    "Estratto Conto": ["estratto conto", "estrato conto", "estratto"],
    "Certificato di Stipendio": ["certificato di stipendio", "certificato stipendio", "cert stipendio", "certificato salario"],
    "Lista movimenti": ["lista movimenti", "lista dei movimenti", "movimenti bancari", "movimenti conto"],
    "Conteggio estintivo": ["conteggio estintivo", "conteggio estinzione", "estintivo"],
    "Piano di Ammortamento": ["piano di ammortamento", "piano ammortamento", "ammortamento", "piano rate"],
    "Conteggio Residuo": ["conteggio residuo", "residuo", "debito residuo", "saldo residuo"],
    "Visura": ["visura", "visura catastale", "visura camerale", "catastale"],
    "Scia": ["scia", "segnalazione certificata", "scia edilizia"],
    "Debito residuo": ["debito residuo", "residuo debito", "saldo debitore", "debito rimanente"],
    "Liberatoria": ["liberatoria", "liberatorio", "svincolo", "liberazione ipoteca"],
    "Compromesso": ["compromesso", "preliminare", "proposta acquisto", "compromeso"]
}

PAROLE_INTENZIONE = ["mando", "invio", "allego", "mandare", "inviare", "mutuo", "prestito", "pratica", "documentazione"]

api = Api(AIRTABLE_TOKEN)
table = api.table(BASE_ID, TABLE_NAME)
table_pratiche = api.table(BASE_ID, "Pratiche")

# ─── FUNZIONI HELPER ──────────────────────────────────────────────────────────
def somiglianza(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def trova_documento_nel_testo(testo, lista_mancanti):
    msg = testo.lower().strip()
    for doc in lista_mancanti:
        sinonimi_doc = SINONIMI.get(doc, [doc.lower()])
        for sinonimo in sinonimi_doc:
            if sinonimo.lower() in msg or somiglianza(sinonimo, msg) > 0.75:
                return doc
    return None

def invia_messaggio_meta(numero, testo):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {META_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": testo}}
    risposta = req.post(url, json=payload, headers=headers)
    return risposta.status_code == 200

def scarica_file_meta(media_id):
    try:
        url_info = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {META_TOKEN}"}
        info = req.get(url_info, headers=headers).json()
        url_file = info.get("url")
        if not url_file: return None, None, None
        file_content = req.get(url_file, headers=headers).content
        ext = ".pdf" if "pdf" in info.get("mime_type", "") else ".jpg"
        return file_content, f"doc_{int(time.time())}{ext}", info.get("mime_type")
    except: return None, None, None

def salva_file_telegram(file_content, nome_file, content_type, mittente):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        risposta = req.post(url, data={"chat_id": TELEGRAM_CHANNEL_ID, "caption": f"Da {mittente}"}, 
                            files={"document": (nome_file, file_content, content_type)})
        res = risposta.json()
        if res.get("ok"):
            f_id = res["result"]["document"]["file_id"]
            info = req.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={f_id}").json()
            return f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{info['result']['file_path']}"
        return None
    except: return None

# ─── WEBHOOK ROUTES ───────────────────────────────────────────────────────────
@app.route("/webhook", methods=["GET"])
def verify():
    # Questa sezione risolve l'errore di convalida di Meta
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verifica fallita", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            msg_obj = data["entry"][0]["changes"][0]["value"]["messages"][0]
            mittente = msg_obj["from"]
            # Logica di gestione messaggi qui (trova cliente, salva file, ecc.)
            # Per brevità ora confermiamo solo la ricezione
            invia_messaggio_meta(mittente, "Messaggio ricevuto dal sistema PraticaOK!")
    except: pass
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
