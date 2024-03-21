const express = require('express');
const path = require('path');
const fs = require('fs');
const multer  = require('multer');
const { SpeechClient } = require('@google-cloud/speech');
const app = express();

GOOGLE_APPLICATION_CREDENTIALS ='C:/Users/aliso/AppData/Roaming/gcloud/application_default_credentials.json';

app.use(express.static('client'));

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname, 'client', 'index.html'));
});

app.post('/speech', function(req, res) {
    console.log("speech received");
});

const server = app.listen(5000, () => {
    console.log("Express server running at port:5000");
});
