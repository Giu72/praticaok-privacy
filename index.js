const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios'); // Serve per "sparare" la risposta verso WhatsApp
const app = express().use(bodyParser.json());

const token = "progetto2024"; 
const WHATSAPP_TOKEN = "IL_TUO_TEMPORARY_ACCESS_TOKEN"; // Prendilo dalla dashboard di Meta

app.get('/webhook', (req, res) => {
    let mode = req.query['hub.mode'];
    let challenge = req.query['hub.challenge'];
    let verify_token = req.query['hub.verify_token'];

    if (mode && verify_token && mode === 'subscribe' && verify_token === token) {
        res.status(200).send(challenge);
    } else {
        res.sendStatus(403);
    }
});

app.post('/webhook', async (req, res) => {
    const body = req.body;

    if (body.object === 'whatsapp_business_account' && body.entry[0].changes[0].value.messages) {
        const from = body.entry[0].changes[0].value.messages[0].from; // Il tuo numero
        const msg_body = body.entry[0].changes[0].value.messages[0].text.body; // Cosa hai scritto
        const phone_number_id = body.entry[0].changes[0].value.metadata.phone_number_id;

        console.log("Messaggio ricevuto da " + from + ": " + msg_body);

        // RISPOSTA AUTOMATICA
        try {
            await axios({
                method: "POST",
                url: `https://graph.facebook.com/v18.0/${phone_number_id}/messages`,
                data: {
                    messaging_product: "whatsapp",
                    to: from,
                    text: { body: "Ricevuto! Sono il tuo nuovo Bot. Hai scritto: " + msg_body },
                },
                headers: { "Authorization": `Bearer ${WHATSAPP_TOKEN}` },
            });
        } catch (err) {
            console.log("Errore invio:", err.response ? err.response.data : err.message);
        }
    }
    res.sendStatus(200);
});

app.listen(process.env.PORT || 10000, () => console.log('Server pronto!'));
