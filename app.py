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

# Token Meta
META_TOKEN = "EAA8G41qOXgUBRZAdyldEJguRRIO7Lbdi8ujyB3BT2vHWcpcDBAqnCCNUu8sv7YMTAa473al52T5B78U8MZCZASdt5FwaMGZBemglb9rnqJZCmYakWfsQ1Y7rGXv62FZArSDD9TEqoNZBhZAxYBnUIU278GIReLLgbbwyW4rHXsYr4VacQZCEvPe6f0yHISueP8p7Gy5vLnIeUmkEGPUHt4VzvQDHVnZAojScZAsObDQO0F0EZAuvEkhfhFPJfRwShLmXuVIFGL8B1e2ABcMrCcW8NlahBT7T"
PHONE_NUMBER_ID = "1156459807541320"

TELEGRAM_TOKEN = "8555023720:AAEpTP9E9EhfpQBra2oSQCIeaeNYdxapv2I"
TELEGRAM_CHANNEL_ID = "-1003939688675"

# ─── SINONIMI ─────────────────────────────────────────────────────────────────
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

PAROLE_INTENZIONE = ["mando", "invio", "allego", "mandare", "inviare", "mutuo",
                     "prestito", "pratica", "documentazione", "buongiorno",
                     "buon", "salve", "ciao", "iniziare", "iniziamo", "ho bisogno"]

# ─── AIRTABLE ─────────────────────────────────────────────────────────────────
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
            if sinonimo.lower() in msg:
                return doc
            if somiglianza(sinonimo, msg) > 0.75:
                return doc
    return None

def get_documenti_per_pratica(tipo_pratica):
    risultati = table_pratiche.all(formula=f"{{Tipo pratica}}='{tipo_pratica}'")
    if risultati:
        return risultati[0]["fields"].get("Documenti richiesti", "")
    return ""

# [QUI ANDREBBERO LE ALTRE FUNZIONI CHE HAI SCRITTO PRIMA: trova_o_crea_cliente, invia_messaggio_meta, ecc.]

# ─── AVVIO ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
