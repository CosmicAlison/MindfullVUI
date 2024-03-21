const express = require('express');
const path = require('path');
const fs = require('fs');
const multer = require('multer');
const openai = require('openai');
const dotenv = require('dotenv').config();
const axio = require('axios');

const app = express();

const upload = multer({ dest: 'uploads/' });

app.use(express.static('client'));

app.get('/', function (req, res) {
    res.sendFile(path.join(__dirname, 'client', 'index.html'));
});

const openaiApiKey = process.env.OPENAI_API_KEY;
const openaiClient = new openai.OpenAI({apiKey: openaiApiKey});

app.post('/upload-audio', upload.single('audio'), async (req, res) => {
    try {
        if (!req.file) {
            throw new Error('No audio file uploaded');
        }

        const audioFilePath = req.file.path;

        const transcription = await transcribeAudio(audioFilePath);
        res.status(200).json({ transcription });
    } catch (error) {
        console.error('Error handling audio file upload:', error);
        res.status(500).json({ error: error.message });
    }
});

async function transcribeAudio(audioFilePath, retries=3) {
    try{const audioFileContent = fs.readFileSync(audioFilePath);

    const response = await openaiClient.audio.transcriptions.create({
        audio: audioFileContent.toString('base64'),
        model: 'whisper-1'
    });

    return response.data.text;
    }
    catch(error){
        if (retries > 0) {
            console.log(`Retrying due to error: ${error.message}`);
            return transcribeAudio(audioFilePath, retries - 1);
        } else {
            throw error;
        }
    }

}

const server = app.listen(5000, () => {
    console.log("Express server running at port:5000");
});
