const express = require('express');
const app = express();
app.use(express.json());

app.get('/webhook', (req, res) => {
  const verify_token = "MIO_TOKEN_SEGRETO"; // Scegli tu una parola
  if (req.query['hub.verify_token'] === verify_token) {
    res.send(req.query['hub.challenge']);
  } else {
    res.sendStatus(403);
  }
});

app.listen(process.env.PORT || 3000, () => console.log('Webhook in ascolto'));
