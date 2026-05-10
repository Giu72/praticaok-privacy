const express = require('express');
const bodyParser = require('body-parser');
const app = express().use(bodyParser.json());

// LA TUA PAROLA D'ORDINE
const token = "progetto2024"; 

// QUESTO SERVE PER "VERIFICA E SALVA"
app.get('/webhook', (req, res) => {
    let mode = req.query['hub.mode'];
    let challenge = req.query['hub.challenge'];
    let verify_token = req.query['hub.verify_token'];

    if (mode && verify_token) {
        if (mode === 'subscribe' && verify_token === token) {
            console.log('WEBHOOK_VERIFIED');
            res.status(200).send(challenge);
        } else {
            res.sendStatus(403);
        }
    }
});

// QUESTO SERVE PER RICEVERE I MESSAGGI
app.post('/webhook', (req, res) => {
    console.log('Messaggio ricevuto:', JSON.stringify(req.body, null, 2));
    res.sendStatus(200);
});

app.listen(process.env.PORT || 10000, () => console.log('Server in ascolto...'));
